## Script (Python) "photo_rotate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=degrees=0,batch=0
##title=Rotate a photo
##
from Products.CMFPlone import transaction_note
qst='portal_status_message=Image+rotated.'
REQUEST=context.REQUEST

context.rotate(degrees=degrees)

tmsg='/'.join(context.portal_url.getRelativeContentPath(context)[:-1])+'/'+context.title_or_id()+' has been modified.'
transaction_note(tmsg)
target_action = context.aq_parent.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?start:int=%s&%s' % ( context.aq_parent.absolute_url()
                                                     , target_action
                                                     , batch
                                                     , qst
                                                     ) )
