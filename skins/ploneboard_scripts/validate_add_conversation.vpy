## Controller Validator "validate_add_conversation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
##


title = context.REQUEST.get('title', '');

if len(title) <= 0:
    state.setError("title", "No title entered", new_status="failure")

if state.getErrors():
    return state.set(portal_status_message='Please correct the indicated errors.')

return state
