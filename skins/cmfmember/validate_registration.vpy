## Controlled Python Script "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None,mail_me=None,password='',confirm_password='',email='',fieldset=None
##title=Validates registration
##

reg_tool=context.portal_registration
properties = context.portal_properties.site_properties
p_len = len(password)

def missing(field):
    state.setError(field, 'Input is required but no input given.', 'input_required')
def nomatch(field):
    state.setError(field, 'Passwords do not match.', 'nomatch_password')
def minlimit(field):
    state.setError(field, 'Passwords must contain at least 5 characters.', 'min_password')

## Username Validators:
if not id and fieldset=='default':
    state.setError('id', 'You did not enter an login name.', 'invalid_id')

if not state.getError('id') and not reg_tool.isMemberIdAllowed(id):
    state.setError('id',
                   'The login name you selected is already in use or is not valid. Please choose another.',
                   'username_invalid' )

## Password Validators:
if not properties.validate_email:

    if p_len == 0:
        state.setError('password','You did not enter a password.','empty_password')
    
    if p_len > 0 and p_len < 5:
        minlimit('password')
        if confirm_password:
            minlimit('confirm_password')
    
    if password == id:
        state.setError('password','You username and password are the same.  This is really not a good idea.','id_pass_same')
    
    if password != confirm_password:
        nomatch('password')
        nomatch('confirm_password')

if not properties.validate_email and not password \
       and not mail_me and fieldset=='default':
    state.setError('password',
                   'You must enter a password or choose to have one mailed to you.',
                   'invalid_password')
    state.setError('mail_me', 
                   'You must enter a password or choose to have one mailed to you.',
                   'invalid_mail_me')

## Email Validators
if not email:
    missing('email')


## Wrapup
if state.getErrors():
    return state.set(status='failure',
                     portal_status_message='Please correct the indicated errors.')
else:
    return state

