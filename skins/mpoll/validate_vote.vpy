## Script (Python) "mboard_validate_vote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a forum contents
##

answer = context.REQUEST.get('answer', None)
if not answer:
    state.setError('answer', 'Please enter a value', new_status='failure')
else:
    try:
        int(answer)
    except:
        state.setError('answer', 'Please enter a integer', new_status='failure')

if state.getErrors():
    state.set(portal_status_message='Please correct the errors shown.')
return state
