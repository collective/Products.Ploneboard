## Controller Python Script "removeI18NLayerFromObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=obj_type_name=None, obj_language=None
##title=Remove I18NLayer from an object
##

from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if not context.insideI18NLayer():
    raise Exception

if obj_type_name is None:
    obj_type_name=context.getTypeInfo().getId()

if obj_language is None:
    obj_language=context.I18nDefaultLanguage()

i18n_container = context.getParentNode()
i18n_id = i18n_container.getId()
folder_container = i18n_container.getParentNode()

# Now copy/paste the content object inside the folder
folder_container.manage_pasteObjects(i18n_container.manage_cutObjects([obj_language,]))

# Delete I18N container
folder_container.manage_delObjects([i18n_id,])

# Finally rename the object 
folder_container.manage_renameObjects((obj_language,), (i18n_id,))

new_context = getattr(folder_container, i18n_id)

portal_status_message = 'multilingual object converted to simple object'
return state.set(context=new_context, portal_status_message=portal_status_message)

