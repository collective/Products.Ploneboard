## Script (Python) "getAmazonCurrentFolder"
##title=Get initial id for an AmazonItem
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

folder = context
while folder:
    if getattr(folder, 'isPrincipiaFolderish', 0):
        return folder
    if folder.meta_type == 'Plone Site':
        folder
    folder = folder.getParentNode()
# from AccessControl import Unauthorized
#
#while not getattr(folder, 'isPrincipiaFolderish', 0):
#    folder = folder.getParentNode()
#if item_folder_id in folder.objectIds():
#    return getattr(folder, item_folder_id)
#try:
#    context.invokeFactory(id=item_folder_id, type_name='Folder')
#    folder.setTitle('Amazon Items')
#    return folder
#except Unauthorized:
#    return folder