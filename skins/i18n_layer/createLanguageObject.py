## Script (Python) "createLanguageObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None,redirect=1
##title=
##
from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if type_name is None:
    raise Exception

if id is None:
    raise Exception


# portal factory support
factory_types = ()
try:
    if hasattr(context, 'portal_factory'):
        factory_types = context.portal_factory.getFactoryTypes()
except: pass
if not type_name in factory_types:
    # no portal factory support
    context.invokeFactory(id=id, type_name=type_name)
    o=getattr(context, id, None)
    transaction_note(o.getTypeInfo().getId() + ' was created.')
else:
    # use portal factory
    o = context.restrictedTraverse('portal_factory/%s/%s' % (type_name, id))

if o is None:
    raise Exception

# make created object an i18nlayer object
context.setI18NLayerAttributes(id, o)

if redirect:
    view=''
    try: view=o.getTypeInfo().getActionById('edit')
    except: view=o.getTypeInfo().getActionById('view')
    return REQUEST.RESPONSE.redirect(o.absolute_url()+'/'+view)
else: return o

