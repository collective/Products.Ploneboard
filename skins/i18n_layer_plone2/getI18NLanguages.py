## Controller Python Script "getI18NLanguages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return available languages
##

languages_list = []
languages = {}

# Test if portal_languages tool exists
try:
    languages_list = context.portal_languages.listSupportedLanguages()
except:
    # So use default languages list
    languages_list = context.availableLanguages()

# Build dictionnary    
for language in languages_list:
    languages[language[0]] = language[1]

return languages

