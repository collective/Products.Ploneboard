## Script (Python) "contentpanels_getPanel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objectPath, panelSkin, panelObjectViewlet
##title=
##

panelObject = context.getPanelObject(objectPath)

# get viewlet infomation
defaultViewletPath = 'here/viewlet_default/macros/portlet'
viewletPath = defaultViewletPath
actions = context.portal_actions.listFilteredActionsFor(panelObject).get('panel_viewlets', [])
for action in actions:
    if action['id'] == panelObjectViewlet: 
      try:
        viewletPath = action['action']
      except:
        viewletPath = action['url']
      break

return panelObject.base_panel(panelObject, 
                              panelSkin=panelSkin, 
                              viewletPath=viewletPath, 
                              panelObjectIsCP = (panelObject == context) )

