## Script (Python) "prefs_user_details"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid=""
##title=
##
#
request = context.REQUEST
RESPONSE =  request.RESPONSE

RESPONSE.redirect('%s/portal_memberdata/%s/base_edit' % \
    (context.portal_url(), userid))
