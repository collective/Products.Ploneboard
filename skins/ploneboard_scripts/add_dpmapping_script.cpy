## Controller Python Script "add_dmapping_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=key, value, transform_name
##title=

dprovider = context.portal_ploneboard.getDataProvider(transform_name)
dprovider.setElement({key : value})

REQUEST = context.REQUEST
REFERER = REQUEST.HTTP_REFERER
if REFERER.find('portal_status_message')!=-1:
    REFERER = REFERER[:REFERER.find('portal_status_message')]
url = '%s&%s' % (REFERER, 'portal_status_message=Data+provider+updated.')
return REQUEST.RESPONSE.redirect(url)
