## Script (Python) "mboard_validate_vote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a forum contents
##
validator = context.portal_form.createForm()
validator.addField('answer', 'Integer', required=1)
errors=validator.validate(context.REQUEST)

if errors:
    return ('failure', errors, {'portal_status_message':'An error occured while processing your vote.'})

return ('success', errors, {'portal_status_message':'Your vote has been registered.'})
