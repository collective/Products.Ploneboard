"""\
This file is an installation script for CMFContentPanels (ZPT skins).  It's meant
to be used as an External Method.  To use, add an external method to the
root of the CMF Site that you want ZPT skins registered in with the
configuration:

 id: install_forum
 title: Install ContentPanels Product *optional*
 module name: CMFContentPanels.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Test' tab.  The install function will execute and give
information about the steps it took to register and install the
ZPT skins into the CMF Site instance. 
"""

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod import ExternalMethod

from Acquisition import aq_base
from cStringIO import StringIO
import string
import string 

from Acquisition import Implicit
import Persistence

from Products.CMFContentPanels import ContentPanels_globals, ContentPanels

def install_SubSkin(self, outStream, skinFolder):
    """ Installs a subskin, should be just 1 folder.
    """
    skinstool=getToolByName(self, 'portal_skins')
    for skin in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skin)
        path = map( string.strip, string.split( path,',' ) )
        if not skinFolder in path:
            try:
                path.insert( path.index( 'custom')+1, skinFolder )
            except ValueError:
                path.append(skinFolder)
            path = string.join( path, ', ' )
            skinstool.addSkinSelection( skin, path )
            outStream.write('CMFContentPanels subskin successfully installed into %s.\n' % skin)    
        else:
            outStream.write('CMFContentPanels subskin was already installed into %s.\n' % skin)    

def install_Skins(self, out):
    """
        Add a new skin, 'Plone', copying 'ZPT', if it exists, and then
        add our directories only to it.
    """

    skinstool = getToolByName(self, 'portal_skins')

    try:
        install_SubSkin(self, out, 'contentpanels')
        install_SubSkin(self, out, 'contentpanels/viewlets')
        install_SubSkin(self, out, 'contentpanels/box_skins')
        out.write('CMFContentPanels subskin successfully installed.\n')
    except:
        out.write('CMFContentPanels subskin failed to install.\n')

    try:  
        addDirectoryViews( skinstool, 'skins', ContentPanels_globals )
        out.write( "Added CMFContentPanels directory views to portal_skins.\n" )
    except:
        out.write( 'Unable to add CMFContentpanels directory view to portal_skins.\n')

def install_Actions(self, out):
    # Set actions
    portal_actions = getToolByName(self, 'portal_actions')
    portal_actions.addActionProvider('portal_contentpanels')

    # global viewlet actions
    # latest_updates_viewlet / news_viewlet
    viewlets = ('latest_updates_viewlet', 'default_viewlet')
    listA = portal_actions.listActions()
    selections = tuple([i for i in range(0,len(listA)) if listA[i].id in viewlets])
    if selections:
        portal_actions.deleteActions(selections)

    # new viewlet actions for types
    actions=({"type":"Document",
              "id":"document_viewlet",
              "name":"Body",
              "action":"here/viewlet_document_body/macros/portlet",
              "condition":"",
              "permission":"View",
              "category":"panel_viewlets",
              "visible":1},
             {"type":"Topic",
              "id":"view_viewlet",
              "name":"Body",
              "action":"here/viewlet_topic_list/macros/portlet",
              "condition":"",
              "permission":"View",
              "category":"panel_viewlets",
              "visible":1},
             {"type":"Image",
              "id":"view_viewlet",
              "name":"Body",
              "action":"here/viewlet_image_body/macros/portlet",
              "condition":"",
              "permission":"View",
              "category":"panel_viewlets",
              "visible":1},
             {"type":"Wiki Page",
              "id":"wiki_page_content",
              "name":"Body",
              "action":"here/viewlet_zwikipage_body/macros/portlet",
              "condition":"",
              "permission":"View",
              "category":"panel_viewlets",
              "visible":1},
             )
    portal_types = getToolByName(self, 'portal_types')
    for action in actions:
       portalType = portal_types.getTypeInfo(action['type'])
       if not portalType:
           continue
       portalTypeActions = portalType.listActions()
       for i in range(0, len(portalTypeActions)):
           try: # is CMF 1.4+ ?
               isExisted = action['id'] == portalTypeActions[i].id
           except:
               isExisted = action['id'] == portalTypeActions[i]['id']
           if isExisted:
               portalType.deleteActions((i,))
               break

       try: # isCMF1_4+ ?
           portalType.addAction(
               id=action['id'],
               name=action['name'],
               action='string:'+action['action'],
               condition=action['condition'],
               permission=action['permission'],
               category=action['category'],
               visible=action['visible'])
       except:
           portalType.addAction(
              id=action['id'],
              name=action['name'],
              action=action['action'],
              permission=action['permission'],
              category=action['category'],
              visible=action['visible'])

    out.write("Actions Setup Done\n")

def install(self):
    """ Register the ContentPanels Skins with portal_skins and friends """
    skinstool = getToolByName(self, 'portal_skins')

    out = StringIO()
    out.write( 'CMFContentPanels installation tool\n')

    install_Skins(self, out)

    # Register with the typestool manually instead of with manage_addTypeInformation
    # as the classes were not registered with utils.ContentInit in __init__.py
    types_tool = getToolByName(self, 'portal_types')
    for t in ContentPanels.factory_type_information:
        if t['id'] not in types_tool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            types_tool._setObject(t['id'], cfm)
            out.write('Registered %s with the types tool\n' % t['id'])
        else:
            out.write('Skipping "%s" - already in types tool\n' % t['id'])

    if not hasattr(self, 'portal_contentpanels'):
        addTool = self.manage_addProduct['CMFContentPanels'].manage_addTool
        addTool('ContentPanels Tool')
        out.write('Added ConentPanels Tool\n')

    install_Actions(self, out)
    return out.getvalue()
