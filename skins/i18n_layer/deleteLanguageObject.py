## Script (Python) "deleteLanguageObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a i18NLayer
##
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

ids=REQUEST.get('ids', None)

if ids:
    transaction_note( str(ids)+' has been deleted' )
    context.manage_delObjects(ids, REQUEST)
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/i18nlayer_languages_form?portal_status_message=Deleted.')

else:
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/i18nlayer_languages_form?portal_status_message=Please+select+one+or+more+items+first.')
