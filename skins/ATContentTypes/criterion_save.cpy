## Controller Python Script "criterion_save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Criterion Save

REQUEST=context.REQUEST
from Products.CMFPlone import transaction_note

criteria = context.listCriteria()

MARKER=[]

for criterion in criteria:
    id  = criterion.getId()
    schematas = criterion.Schemata()
    fields = [field for field in schematas['default'].fields()
                    if field.mode != 'r' ]

    for field in fields:
        fid = '%s_%s' % (id, field.getName())
        rval = REQUEST.get(fid, MARKER)
        accessor = field.getAccessor(criterion)
        if rval is not MARKER and accessor() != rval:
            mutator = field.getMutator(criterion)
            mutator(rval)

msg='Changes saved'
transaction_note(msg)

return state.set(portal_status_message=msg)
