## Script (Python) "setDisplayCookie"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=display, b_start
##title=
##

request = context.REQUEST
response = context.REQUEST.RESPONSE

response.setCookie('photoalbum_display', display, expires='Wed, 19 Feb 2020 14:28:00 GMT', path='/')

response.redirect(request.get('URL1') + '/photoalbum_photo_view?b_start=%s' % (b_start,))
