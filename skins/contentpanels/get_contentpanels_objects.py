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
patched_content_boxes = []
for id, title in content_boxes:
    # patch for zwikis pages in the same folder
    # in that case, listFolderContents returns wrong tuples like
    # , (<bound method ZWikiPage.name of <ZWikiPage 'FrontPage' at 0x8850c48>>, 'FrontPage')
    if callable(id):
        id = id()
    patched_content_boxes.append((id, title))

return patched_content_boxes + getCopyedObjectsInfo(context, context.REQUEST)


