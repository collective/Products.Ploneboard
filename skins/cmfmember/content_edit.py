## Script (Python) "content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None

obj = context.portal_factory.doCreate(context, id)
obj.processForm()

return ('success', obj, {'portal_status_message':context.REQUEST.get('portal_status_message', 'Content changes saved.')})
