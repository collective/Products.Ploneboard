## Script (Python) "createPhotoAlbumInstance"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=
##

context.invokeFactory(type_name='Photo Album', id=id)
