## Script (Python) "do_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id, password=None
##title=Registered
##
#(status, new_context, args) = context.restrictedTraverse('content_edit')()
(status, new_context, args) = apply(context.content_edit, (), {'id':id})
portal = context.portal_url.getPortalObject()
return (status, portal, {'portal_status_message':'You have been registered.','id':id,'password':password})
