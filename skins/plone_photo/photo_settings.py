## Script (Python) "photo_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=display
##title=Save settings for this product
##
qst='portal_status_message=Settings+saved.'

context.REQUEST.RESPONSE.setCookie('display', display, expires='Wed, 19 Feb 2020 14:28:00 GMT', path='/')

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
