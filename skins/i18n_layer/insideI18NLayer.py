## Script (Python) "insideI18NLayer"
##title=
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
REQUEST=context.REQUEST

try:
    parent = context.aq_parent
except:
    parent = None

if parent and getattr(parent, 'meta_type', None) == 'I18NLayer':
    return 1
else:
   return 0
