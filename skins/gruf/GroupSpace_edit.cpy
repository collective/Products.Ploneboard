## Script (Python) "GroupSpaceFolderishType_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='', title=None, description=None
##title=Edit a GroupSpace
##

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

# Custom editing method (called only for specific attributes)
#    ( GroupSpaceFolderishType doesn't derive Metadata so title is not
#      a metadata information )
new_context.edit(title = title)

# Generic editing method (ie. edits id + Metadata)
new_context.plone_utils.contentEdit(
    new_context,
    id = id,
    )

return state.set(portal_status_message = "GroupSpace changes saved.")

