## Controller Python Script "criterion_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=field, criterion_type
##title=Criterion Add

REQUEST=context.REQUEST
from Products.CMFPlone import transaction_note

context.addCriterion(field, criterion_type)

msg = 'Added criterion %s for field %s' % (criterion_type, field)
transaction_note(msg)

return state.set(portal_status_message=msg)
