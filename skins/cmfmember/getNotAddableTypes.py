## Script (Python) "getNotAddableTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#
if not 'portal_memberdata' in context.getPhysicalPath():
    return ('Favorite',)
else:
    checkPermission = context.portal_membership.checkPermission
    if not checkPermission('Manage users', context):
        return tuple(context.allowed_content_types)
    else:
        return tuple()
