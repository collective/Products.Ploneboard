## Script (Python) "get_contentpanels_objects"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

from Products.CMFContentPanels.ContentPanels import getCopyedObjectsInfo

folder_contents = context.listFolderContents()
content_boxes = [ (item.id, item.Title() )for item in folder_contents]

return content_boxes + getCopyedObjectsInfo(context, context.REQUEST)

