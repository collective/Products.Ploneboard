## Script (Python) "change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=password, confirm, domains=None
##title=Change password
##

pass

## This code is there because there's a bug in CMF that prevents
## passwords to be changed if the User Folder doesn't store it in a __
## attribute.
## This includes User Folders such as LDAPUF, SimpleUF, and, of course, GRUF.
## This also includes standard UF with password encryption !

mt = context.portal_membership
failMessage=context.portal_registration.testPasswordValidity(password, confirm)

if failMessage:
  return context.password_form(context,
                               context.REQUEST,
                               error=failMessage)
context.REQUEST.AUTHENTICATED_USER.changePassword(password)
mt.credentialsChanged(password)
return context.personalize_form(context,
                                context.REQUEST,
                                portal_status_message='Password changed.')

