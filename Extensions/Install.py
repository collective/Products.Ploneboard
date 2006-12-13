"""\
$Id$

This file is an installation script for Ploneboard.  It's meant to be
used as an External Method.  To use, add an external method to the
root of the Plone Site that you wantPloneboard registered in with the
configuration:

 id: install_ploneboard
 title: Install Ploneboard *optional*
 module name: Ploneboard.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the
Ploneboard into the Plone Site instance. 
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.TypesTool import ContentFactoryMetadata

from cStringIO import StringIO
import string

from Products.Archetypes.public import listTypes, process_types
from Products.Archetypes.ArchetypeTool import getType
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Ploneboard.config import PLONEBOARD_TOOL, PROJECTNAME, GLOBALS
from Products.Ploneboard.config import EMOTICON_TRANSFORM_MODULE, \
                                       URL_TRANSFORM_MODULE, \
                                       SAFE_HTML_TRANSFORM_MODULE
from Products.Archetypes.config import TOOL_NAME, UID_CATALOG

from Products.Ploneboard.permissions import AddAttachment
from Products.Ploneboard.migrations import migrate01b1to10b

from StringIO import StringIO


configlets = \
( { 'id'         : 'Ploneboard'
  , 'name'       : 'Ploneboard Setup'
  , 'action'     : 'string:${portal_url}/prefs_ploneboard_form'
  , 'category'   : 'Products'
  , 'appId'      : 'Ploneboard'
  , 'permission' : ManagePortal
  , 'imageUrl'  : 'ploneboard_icon.gif'
  }
,
)

def migrateTransforms(self, out):
    tool = getToolByName(self, PLONEBOARD_TOOL)
    if not hasattr(tool, 'transforms'):
        from ZODB.PersistentMapping import PersistentMapping
        tool.transforms = PersistentMapping()
        out.write('Adding transforms registry\n')

    if hasattr(tool, 'transforms_config'):
        for (key,value) in tool.transforms_config.items():
            tool.transforms[key] = {
                    'enabled' : value['transform_status'],
                    'friendlyName' : key,
                    'wasAdded' : True
                    }
        del tool.transforms_config
        out.write('Migrated transform configuration\n') 

def addPloneboardTool(self, out):
    if not hasattr(self, PLONEBOARD_TOOL):
        addTool = self.manage_addProduct['Ploneboard'].manage_addTool
        addTool('Ploneboard Tool')
        out.write('Added Ploneboard Tool\n')

def addCatalogIndices(self, out):
    pc=getToolByName(self, 'portal_catalog')
    if 'object_implements' not in pc.indexes():
        pc.addIndex('object_implements', 'KeywordIndex')
        out.write('Added object_implements index to portal_catalog\n')
    if 'num_comments' not in pc.indexes():
        pc.addIndex('num_comments', 'FieldIndex')
        out.write('Added num_comments index to portal_catalog\n')

def registerNavigationTreeSettings(self, out):
    data = ['PloneboardConversation','PloneboardComment']
    pp=getToolByName(self,'portal_properties')
    p = getattr(pp , 'navtree_properties', None)
    mdntl = list(p.getProperty('metaTypesNotToList', None))
    if mdntl is None:
        p._setProperty('metaTypesNotToList', data)
    else:
        for t in data:
            if t not in mdntl:
                mdntl.append(t)
        p._updateProperty('metaTypesNotToList', mdntl)

def setupPloneboardWorkflow(self, out):
    wf_tool=getToolByName(self, 'portal_workflow')
    default_chain = wf_tool._default_chain
    cbt = wf_tool._chains_by_type

    if 'ploneboard_comment_workflow' in wf_tool.objectIds():
        out.write('Removing existing Comment Workflow\n')
        wf_tool._delObject('ploneboard_comment_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_comment_workflow'
                              , workflow_type='ploneboard_comment_workflow '+\
                                '(Comment Workflow [Ploneboard])')
    if not cbt.has_key('PloneboardComment'):
        wf_tool.setChainForPortalTypes( ('PloneboardComment',), 'ploneboard_comment_workflow')
    out.write('Added Comment Workflow\n')

    if 'ploneboard_conversation_workflow' in wf_tool.objectIds():
        out.write('Removing existing Conversation Workflow\n')
        wf_tool._delObject('ploneboard_conversation_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_conversation_workflow'
                              , workflow_type='ploneboard_conversation_workflow '+\
                                '(Conversation Workflow [Ploneboard])')
    if not cbt.has_key('PloneboardConversation'):
        wf_tool.setChainForPortalTypes( ('PloneboardConversation',), 'ploneboard_conversation_workflow')
    out.write('Added Conversation Workflow\n')

    if 'ploneboard_forum_workflow' in wf_tool.objectIds():
        out.write('Removing existing Forum Workflow\n')
        wf_tool._delObject('ploneboard_forum_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_forum_workflow'
                              , workflow_type='ploneboard_forum_workflow '+\
                                '(Forum Workflow [Ploneboard])')
    if not cbt.has_key('PloneboardForum'):
        wf_tool.setChainForPortalTypes( ('PloneboardForum',), 'ploneboard_forum_workflow')
    out.write('Added Forum Workflow\n')

    if 'ploneboard_workflow' in wf_tool.objectIds():
        out.write('Removing existing Ploneboard Workflow\n')
        wf_tool._delObject('ploneboard_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_workflow'
                              , workflow_type='ploneboard_workflow '+\
                                '(Ploneboard Workflow [Ploneboard])')
    if not cbt.has_key('Ploneboard'):
        wf_tool.setChainForPortalTypes( ('Ploneboard',), 'ploneboard_workflow')
    out.write('Added Ploneboard Workflow\n')

def addPortalProperties(self, out):
    data = ['PloneboardConversation']
    pp=getToolByName(self,'portal_properties')
    p = getattr(pp , 'site_properties', None)
    tns = list(p.getProperty('types_not_searched', []))
    if not tns:
        p._setProperty('types_not_searched', data)
    else:
        for t in data:
            if t not in tns:
                tns.append(t)
                out.write("Added %s to types_not_searched\n" % t)
        p._updateProperty('types_not_searched', tns)

def addConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        lets = [c['id'] for c in configTool.enumConfiglets(group='Products')]
        for conf in configlets:
            if conf['id'] not in lets:
                out.write('Adding configlet %s\n' % conf['id'])
                configTool.registerConfiglet(**conf)

def addMemberProperties(self, out):
    pass

def addTransforms(self, out):
    pb_tool = getToolByName(self, 'portal_ploneboard')
    pb_tool.registerTransform('text_to_emoticons', EMOTICON_TRANSFORM_MODULE, 'Graphical smilies')
    pb_tool.registerTransform('url_to_hyperlink', URL_TRANSFORM_MODULE, 'Clickable links')
    pb_tool.registerTransform('safe_html', SAFE_HTML_TRANSFORM_MODULE, 'Remove dangerous HTML')

def removeTransforms(self, out):
    pb_tool = getToolByName(self, 'portal_ploneboard')
    try:
        pb_tool.unregisterAllTransforms()
    except (KeyError, AttributeError):
        # This gets raised if your instance is based on Ploneboard 0.1b1
        print >> out, u"It looks like your Ploneboard instance is based on 0.1b1. Unregistering transforms has failed."

def registerTypesWithPortalFactory(self, out): 
    #This assumes we can use portal_factory for all types
    portal_factory = getToolByName(self, 'portal_factory') 
    if portal_factory is not None: 
        factoryTypes = list(portal_factory.getFactoryTypes().keys())
        types = [t['portal_type'] for t in listTypes(PROJECTNAME)]
        for factoryType in types:
            if factoryType not in factoryTypes:
                out.write('Added %s to Portal Factory\n' % factoryType)
                factoryTypes.append(factoryType)
        portal_factory.manage_setPortalFactoryTypes(listOfTypeIds = factoryTypes) 
    else: 
        out.write('Couldn\'t get Portal Factory, so couldn\'t add Ploneboard types to it\n') 

def setupRootPermissions(self, out):
    root = getToolByName(self, 'portal_url').getPortalObject()
    root.manage_permission(AddAttachment, ('Member', 'Manager',), 0)

def removeOldCatalog(self, out):
    at_tool = getToolByName(self, 'archetype_tool')
    catalog = getattr(self, 'ploneboard_catalog', None)
    if catalog is not None and catalog.meta_type == 'Broken Because Product is Gone':
        meta_types = [
            'Ploneboard',
            'PloneboardConversation',
            'PloneboardComment',
            'PloneboardForum',
        ]
        for meta_type in meta_types:
            catalogs = at_tool.getCatalogsByType(meta_type)
            if 'ploneboard_catalog' in catalogs:
                catalogs.remove('ploneboard_catalog')
                at_tool.setCatalogsByType(meta_type, catalogs)
                out.write('Unselected ploneboard_catalog for %s.\n' % meta_type)
        self._delObject('ploneboard_catalog')
        out.write('Removed old ploneboard_catalog object.\n')

def automigrate(self, out):
    qi_tool = getToolByName(self, 'portal_quickinstaller')
    code_version = qi_tool.getProductVersion('Ploneboard')
    installed_prod = getattr(qi_tool, 'Ploneboard', None)
    if installed_prod is None:
        instance_version = code_version
    else:
        instance_version = installed_prod.getInstalledVersion()
    if instance_version != code_version:
        # XXX This is rather brittle; it only knows about migrating from 0.1b1 to 1.0b!
        # Better code here would figure out if the instance_version is any release in
        # the 1.0 series, and then skip the migration call.
        # However, it *is* safe to make multiple calls to the migration, so you are only
        # wasting a few cycles.
        migration = migrate01b1to10b.Migration(self, out).migrate()
    else:
        msg = u"No migration necessary."
        print >> out, msg

def install(self, reinstall=False):
    out = StringIO()

    addPloneboardTool(self, out)
    addCatalogIndices(self, out)

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    registerNavigationTreeSettings(self, out)
    registerTypesWithPortalFactory(self, out)

    setupPloneboardWorkflow(self, out)
    addPortalProperties(self, out)
    addConfiglets(self, out)
    addMemberProperties(self, out)

    # Not sure when is best to make this call, but it works here ;-).
    automigrate(self, out)
    removeOldCatalog(self, out)
    migrateTransforms(self, out)
    addTransforms(self, out)

    setupRootPermissions(self, out)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()


#
# Uninstall methods
#
def removeConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Removing configlet %s\n' % conf['id'])
            configTool.unregisterConfiglet(conf['id'])

# The uninstall is used by the CMFQuickInstaller for uninstalling.
# CMFQuickInstaller uninstalls skins.
def uninstall(self):
    out=StringIO()
    removeConfiglets(self, out)
    removeTransforms(self, out)
        
    return out.getvalue()
