## Script (Python) "contentpanels_getViewletActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objectPath
##title=
##

panelObject = context.getPanelObject(objectPath)

viewletActions = context.portal_actions.listFilteredActionsFor(panelObject).get('panel_viewlets', [])
return viewletActions

