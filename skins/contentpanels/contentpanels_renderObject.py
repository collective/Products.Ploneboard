## Script (Python) "contentpanels_renderObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

panel_viewer = ''

# 1. try to use the action view with name 'contentpanel_view'

try:
  panel_viewer = context.getTypeInfo().getActionById('contentpanel_view')
except:

# 2. try to find the view in the registry :)

  if context.contentpanels_panelviewer_registry().has_key(context.getPortalTypeName() ):
    panel_viewer = context.contentpanels_panelviewer_registry()[context.getPortalTypeName()]
  elif context.contentpanels_panelviewer_registry().has_key(context.getTypeInfo().Metatype() ):
    panel_viewer = context.contentpanels_panelviewer_registry()[context.getTypeInfo().Metatype()]

# 3. can't find, use default ugly panel viwer
if panel_viewer == '':
  panel_viewer = 'contentpanels_defualt_panelviewer'

# panelcontent = apply(context.restrictedTraverse(panel_viewer), (context, None) )

try:
  panelcontent = apply(context.restrictedTraverse(panel_viewer), (context, None) )
except:
  panelcontent = 'Sorry, Exception while render this Page.'

return panelcontent
