## Controller Python Script "I18NContentEdit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=lang_code=None
##title=
##

if not lang_code:
    raise Exception

parent = context.getParentNode()
defined_langs = context.getI18NDefinedLanguages()
url = ''
bcreate = 0

if lang_code not in defined_langs.keys():
    bcreate = 1

if context.insideI18NLayer():
    if bcreate:
        return context.addI18NLanguageObject(obj_language=lang_code)
    else:
        url = parent.absolute_url() + '/' + lang_code + '/view'
else:
    if bcreate:
        id = context.getId()
        context.addI18NLayerToObject(obj_language=defined_langs.keys()[0])
        i18nlayer = getattr(parent, id)
        obj = getattr(i18nlayer, defined_langs.keys()[0])
        return obj.addI18NLanguageObject(obj_language=lang_code)
    else:
        url = 'view'

url = 'redirect_to:string:' + url

state.setNextAction(url)

return state

