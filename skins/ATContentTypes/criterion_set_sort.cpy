## Controller Python Script "criterion_set_sort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=field, reversed=0
##title=Criterion Set Sort

REQUEST=context.REQUEST
from Products.CMFPlone import transaction_note

if field == 'no_sort':
    context.removeSortCriterion()
else:
    context.setSortCriterion(field, reversed)

msg = 'Sort order set on field %s' % (field)
transaction_note(msg)

return state.set(portal_status_message=msg)
