## Script (Python) "i18nlayer_check4tab"
##title=check if the translate tab shall be shown
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object=None
REQUEST=context.REQUEST

if not object: object=context

if getattr(object.aq_explicit, 'meta_type', None) == 'I18NLayer': return 0

try: layer = object.retrieveI18NContentLayerOb()
except: return 0

if not context.portal_membership.checkPermission('Add portal content', layer): return 0

return 1
