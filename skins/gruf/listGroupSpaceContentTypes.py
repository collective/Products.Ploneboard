## Script (Python) "listGroupSpaceContentTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

result = []
portal_types = container.portal_types
result = portal_types.listTypeInfo()

ret = map(lambda x: x.getId(), result)
ret = filter(lambda x: x != 'GroupSpace', ret)
return ret


