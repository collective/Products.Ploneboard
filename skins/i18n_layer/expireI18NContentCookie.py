## Script (Python) "expireI18NContentCookie"
##title=
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None

if not REQUEST:
    REQUEST=context.REQUEST

if REQUEST.cookies.get('I18N_CONTENT_LANGUAGE', None):
    REQUEST.RESPONSE.expireCookie('I18N_CONTENT_LANGUAGE',path='/')

