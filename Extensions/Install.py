"""\
$Id: Install.py,v 1.3 2003/12/12 01:35:47 alienoid Exp $

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

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Ploneboard.config import *
from Products.Archetypes.config import TOOL_NAME, UID_CATALOG

from StringIO import StringIO


configlets = \
( { 'id'         : 'Ploneboard'
  , 'name'       : 'Configure Ploneboard'
  , 'action'     : 'string:${portal_url}/prefs_ploneboard_form'
  , 'category'   : 'Products'
  , 'appId'      : 'Ploneboard'
  , 'permission' : ManagePortal
  , 'imageUrl'  : 'ploneboard_icon.gif'
  }
,
)

def addPloneboardTool(self, out):
    if not hasattr(self, 'portal_ploneboard'):
        addTool = self.manage_addProduct['Ploneboard'].manage_addTool
        addTool('Ploneboard Tool')
        out.write('Added Ploneboard Tool\n')
        
def setupAdditionalTypes(self, out):
    from Products.Ploneboard.PloneboardForum import factory_type_information as pf_fti
    from Products.Ploneboard.PloneboardConversation import factory_type_information as pc_fti
    from Products.Ploneboard.PloneboardMessage import factory_type_information as pm_fti
    
    fti_list = pf_fti + pc_fti + pm_fti

    typesTool = getToolByName(self, 'portal_types')
    
    # Former types deletion (added by PJG)
    for f in fti_list:
        if f['id'] in typesTool.objectIds():
            out.write('*** Object "%s" already existed in the types tool => deleting\n' % (f['id']))

            typesTool._delObject(f['id'])

    # Type re-creation
    for f in fti_list:
        cfm = apply(ContentFactoryMetadata, (), f)
        typesTool._setObject(f['id'], cfm)
        out.write('Type "%s" registered with the types tool\n' % (f['id']))

def setupPloneboardWorkflow(self, out):
    wf_tool=getToolByName(self, 'portal_workflow')
    if 'ploneboard_message_workflow' in wf_tool.objectIds():
        out.write('Removing existing Message Workflow\n')
        wf_tool._delObject('ploneboard_message_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_message_workflow'
                              , workflow_type='ploneboard_message_workflow '+\
                                '(Message Workflow [Ploneboard])')
    wf_tool.setChainForPortalTypes( ('PloneboardConversation','PloneboardMessage'), 'ploneboard_message_workflow')
    out.write('Added Message Workflow\n')

    if 'ploneboard_forum_workflow' in wf_tool.objectIds():
        out.write('Removing existing Forum Workflow\n')
        wf_tool._delObject('ploneboard_forum_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_forum_workflow'
                              , workflow_type='ploneboard_forum_workflow '+\
                                '(Forum Workflow [Ploneboard])')
    wf_tool.setChainForPortalTypes( ('PloneboardForum',), 'ploneboard_forum_workflow')
    out.write('Added Forum Workflow\n')

    if 'ploneboard_workflow' in wf_tool.objectIds():
        out.write('Removing existing Ploneboard Workflow\n')
        wf_tool._delObject('ploneboard_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_workflow'
                              , workflow_type='ploneboard_workflow '+\
                                '(Ploneboard Workflow [Ploneboard])')
    wf_tool.setChainForPortalTypes( ('Ploneboard',), 'ploneboard_workflow')
    out.write('Added Ploneboard Workflow\n')

def addPortalProperties(self, out):
    # Add properties which are used throughout the site.
    #portal._setProperty('variable',  'value', 'type')

    out.write("Added properties to portal\n")

    # set up variables for members
    #portal_memberdata._setProperty('variable', 'value', 'type' )

    out.write("Added member variables\n")

def addConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Adding configlet %s\n' % conf['id'])
            configTool.registerConfiglet(**conf)

def addMemberProperties(self, out):
    pass

def addTransforms(self, out):
    pb_tool = getToolByName(self, 'portal_ploneboard')
    pb_tool.registerTransform('text_to_emoticons', EMOTICON_TRANSFORM_MODULE)
    pb_tool.registerTransform('url_to_hyperlink', URL_TRANSFORM_MODULE)
    
def removeTransforms(self, out):
    pb_tool = getToolByName(self, 'portal_ploneboard')
    pb_tool.unregisterAllTransforms()
    
def install(self):
    out = StringIO()
    
    addPloneboardTool(self, out)

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    
    setupAdditionalTypes(self, out)
    
    # Here we exclude our types to be cataloged in portal_catalog by archetypes
    # we need only UID_CATALOG from archetypes
    at = getToolByName(self, TOOL_NAME)
    for type in listTypes(PROJECTNAME):
        if type['name'] != 'Ploneboard': # Let Ploneboard object be in portal_catalog
            at.setCatalogsByType(type['name'], [UID_CATALOG])

    install_subskin(self, out, GLOBALS)
    
    setupPloneboardWorkflow(self, out)
    addPortalProperties(self, out)
    addConfiglets(self, out)
    addMemberProperties(self, out)
    
    addTransforms(self, out)

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