## Script (Python) "contentpanels_edit_property"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='', title=None, description=None, customCSS=''
##title=Edit contentpanels property
##

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.edit(customCSS)

new_context.plone_utils.contentEdit(new_context
                               , id=id
                               , title=title
                               , description=description)
return state.set(status='success',\
                 context=new_context,\
                 portal_status_message='contentpanels property changes saved.')
