## Controller Validator "validate_posting"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
##

validator = context.portal_form.createForm()
validator.addField('text', 'String', required=1)
errors = validator.validate(context.REQUEST)

for fieldid, error in errors.items():
    state.setError(fieldid, error)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
if context.REQUEST.get('edit',[]):
    return state.set(status='failure')
else:
    return state
