## Controller Python Script "getI18NDefaultLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return I18N default language
##

return context.portal_properties.site_properties.default_language

