## Script (Python) "translate_sheet"
##title=display the translate sheet of the current i18nlayer
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
REQUEST=context.REQUEST

layer = context.retrieveI18NContentLayerOb()

a = context.portal_actions.listFilteredActionsFor(layer).items()
a = map(lambda x: x[1], a)
                                                                                                 
actions=[]
for x in a: actions=actions+x

url=None
for action in actions:
    if action.get('id', '').lower() == 'languagelisting':
        url = action.get('url', None)

if not url: url=layer.absolute_url()+'/i18nlayer_languages_form'

REQUEST.RESPONSE.redirect(url)
