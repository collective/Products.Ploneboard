"""\
$Id: Install.py,v 1.1 2003/10/24 13:03:06 tesdal Exp $

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

from Products.Ploneboard import Ploneboard, Forum, Conversation, Message, ploneboard_globals

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

from cStringIO import StringIO
import string

fti_list = Ploneboard.factory_type_information + \
           Forum.factory_type_information + \
           Conversation.factory_type_information + \
           Message.factory_type_information

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

def setupTypesandSkins(self, out):
    # Add our tool
    try:
        addTool = self.manage_addProduct['Ploneboard'].manage_addTool
        addTool('Ploneboard Tool')
        out.write('Adding Ploneboard Tool\n')
    except:
        out.write('Ploneboard Tool already existed, skipping...\n')
    
    typesTool = getToolByName(self, 'portal_types')
    skinsTool = getToolByName(self, 'portal_skins')
    
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

        
    # Add directory views
    try:  
        addDirectoryViews(skinsTool, 'skins', ploneboard_globals)
        out.write( "Added directory views to portal_skins.\n" )
    except:
        out.write( '*** Unable to add directory views to portal_skins.\n')

    # Go through the skin configurations and insert 'ploneboard_templates'  and
    # ploneboard_scripts into the configurations.
    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        changed = 0
        if 'ploneboard_templates' not in path:
            try: 
                path.insert(path.index('custom')+1, 'ploneboard_templates')
                changed = 1
            except ValueError:
                path.append('ploneboard_templates')
                changed = 1

        if 'ploneboard_scripts' not in path:
            try: 
                path.insert(path.index('custom')+1, 'ploneboard_scripts')
                changed = 1
            except ValueError:
                path.append('ploneboard_scripts')
                changed = 1
                
        if changed:        
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinsTool.addSkinSelection(skin, path)
            out.write("Added 'ploneboard_templates' and/or 'ploneboard_scripts' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'ploneboard_templates' and 'ploneboard_scripts' already set up\n" % (
                skin))


def setupPloneboardWorkflow(self, out):
    wf_tool=getToolByName(self, 'portal_workflow')
    if 'ploneboard_message_workflow' in wf_tool.objectIds():
        out.write('Removing existing Message Workflow\n')
        wf_tool._delObject('ploneboard_message_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_message_workflow'
                              , workflow_type='ploneboard_message_workflow '+\
                                '(Message Workflow [Ploneboard])')
    wf_tool.setChainForPortalTypes( ('Ploneboard Conversation','Ploneboard Message'), 'ploneboard_message_workflow')
    out.write('Added Message Workflow\n')

    if 'ploneboard_forum_workflow' in wf_tool.objectIds():
        out.write('Removing existing Forum Workflow\n')
        wf_tool._delObject('ploneboard_forum_workflow')
    wf_tool.manage_addWorkflow( id='ploneboard_forum_workflow'
                              , workflow_type='ploneboard_forum_workflow '+\
                                '(Forum Workflow [Ploneboard])')
    wf_tool.setChainForPortalTypes( ('Ploneboard Forum',), 'ploneboard_forum_workflow')
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
    configTool = getToolByName(self, 'portal_control_panel_actions', None)
    if configTool:
        for conf in configlets:
            out.write('Adding configlet %s\n' % conf['id'])
            configTool.registerConfiglet(**conf)

def addMemberProperties(self, out):
    pass


def install(self):
    out=StringIO()
    setupTypesandSkins(self, out)
    setupPloneboardWorkflow(self, out)
    addPortalProperties(self, out)
    addConfiglets(self, out)
    addMemberProperties(self, out)
    out.write('Installation completed.\n')
    return out.getvalue()

#
# Uninstall methods
#
def removeConfiglets(self, out):
    configTool = getToolByName(self, 'portal_control_panel_actions', None)
    if configTool:
        for conf in configlets:
            out.write('Removing configlet %s\n' % conf['id'])
            configTool.unregisterConfiglet(conf['id'])

# The uninstall is used by the CMFQuickInstaller for uninstalling.
# CMFQuickInstaller uninstalls skins.
def uninstall(self):
    out=StringIO()
    removeConfiglets(self, out)
    return out.getvalue()