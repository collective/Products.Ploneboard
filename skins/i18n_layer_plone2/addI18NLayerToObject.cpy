## Controller Python Script "addI18NLayerToObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None, obj_type_name=None, obj_language=None
##title=Add an I18NLayer to object
##


from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if id is None:
    id=context.getId()

if obj_type_name is None:
    obj_type_name=context.getTypeInfo().getId()

if obj_language is None:
    obj_language=context.I18nDefaultLanguage()

obj_container = context.getParentNode()

# Rename the object to the corresponding language code, in order to move it inside the layer
# Seems this is needed with the current I18NLayer API
obj_container.manage_renameObjects((id,), (obj_language,))

layer_id = context.invokeFactory(id=id, type_name='I18NLayer')
if layer_id is None or layer_id == '':
    layer_id = id
layer = getattr(obj_container, layer_id, None)
transaction_note('Created I18NLayer with id %s in %s' % (layer_id, obj_container.absolute_url()))

if layer is None:
    raise Exception

# Now copy/paste the content object inside the layer
layer.manage_pasteObjects( obj_container.manage_cutObjects([obj_language,]) )

# Finally delete the old version
#obj_container.manage_delObjects([obj_language,])

new_context = getattr(layer, obj_language)

transaction_note('Content object %s has been translated to language %s, see %s' % (id, obj_language, new_context.absolute_url()))

portal_status_message = 'Content object translated'
return state.set(context=new_context, portal_status_message=portal_status_message)

