## Controller Validator "validate_add_comment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
##


text = context.REQUEST.get('text', '');

if len(text) <= 0:
	state.setError("text", "No content entered", new_status="failure")
	
if state.getErrors():
    return state.set(portal_status_message='Please correct the indicated errors.')

return state
