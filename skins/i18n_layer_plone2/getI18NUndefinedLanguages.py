## Controller Python Script "getI18NUndefinedLanguages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get undefined languages
##

langs = {}

if not context.insideI18NLayer():
    def_lang = context.getI18NDefaultLanguage()
    lang = context.getI18NLanguages().get(def_lang, None)
 
    if lang:
        langs = context.getI18NLanguages()
        del(langs[def_lang])
        return langs
    else:
        raise Exception

obj_container = context.getParentNode()
folder_contents = obj_container.getFolderContents()
folder_langs = []

# Get all created languages
for item in folder_contents:
    id = item.getId()
    folder_langs.append(id)

# Build unused languages list
for lang in context.getI18NLanguages().items():
    if lang[0] not in folder_langs:
        langs[lang[0]] = lang[1]

return langs

