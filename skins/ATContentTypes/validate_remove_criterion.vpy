## Script (Python) "validate_remove_criterion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
request = context.REQUEST
criterion_ids=request.get('criterion_ids')
if not criterion_ids:
    msg = 'You must first select a criterion to remove.'
    return state.set(status='failure', portal_status_message=msg )
else:
    return state.set(status='success')
