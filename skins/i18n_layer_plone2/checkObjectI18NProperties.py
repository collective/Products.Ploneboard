## Script (Python) "checkObjectI18NProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Check if object can be I18Nize
##

# Get I18NLayer Type object
i18nlayer = context.portal_types.getTypeInfo('I18NLayer')

# Get context type 
type_info = context.getTypeInfo().getId()
return i18nlayer.allowType(type_info)
