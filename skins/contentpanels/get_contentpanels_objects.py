## Script (Python) "get_contentpanels_objects"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

from Products.CMFContentPanels.ContentPanels import getCopyedObjectsInfo

portlets_found = context.portal_catalog( {'portal_type': ['CMFForum', 'KnowlegeBase']})                                                
purl = context.portal_url()
content_boxes = [ (brain.getPath(),brain.Title )for brain in portlets_found]

return content_boxes + getCopyedObjectsInfo(context, context.REQUEST)

