## Script (Python) "change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Action to change password
##parameters=password, confirm, domains=None

mt = context.portal_membership
member = mt.getAuthenticatedMember()

if context.REQUEST.form.has_key('cancel'):
    context.REQUEST.set('portal_status_message', 'Password change was canceled.')
    return member.personalize_form()
#    return context.personalize_form()

failMessage=context.portal_registration.testPasswordValidity(password, confirm)
if failMessage:
    context.REQUEST.set('portal_status_message', failMessage)
    return context.password_form(context,
                                 context.REQUEST,
                                 error=failMessage)

mt.setPassword(password, domains)
mt.credentialsChanged(password)

url='%s/portal_form/%s?portal_status_message=%s' % ( member.absolute_url()
                                      , 'personalize_form'
                                      , 'Password+changed.' )

return context.REQUEST.RESPONSE.redirect(url)
