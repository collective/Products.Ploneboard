## Script (Python) "validate_GroupSpaceContentType_Edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a GroupSpaceFolderishType edit
##

validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
errors=validator.validate(context.REQUEST)
# Plone2: add from here...
for fieldid, error in errors.items():
    state.setError(fieldid, error)
# ...to here

if state.getErrors():           # Plone2: changed errors to state.getErrors()
    message = 'Please correct the indicated errors.'
    # return ('failure', errors, {'portal_status_message':message})
    return state.set(
      status = 'failure',
      portal_status_message = message,
    )
else:
    message = 'Your changes have been saved.'
    # return ('success', errors, {'portal_status_message':message})
    return state
