## Script (Python) "validate_set_sort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
request = context.REQUEST
indexId=request.get('field')
if indexId == 'no_sort':
    return state.set(status='success')
supported = context.validateAddCriterion(indexId, 'ATSortCriterion')
if not supported:
    msg = 'Sort order on field ' +\
          '"%s" not set, it cannot be used for ordering.' % (indexId)
    return state.set(status='failure', portal_status_message=msg )
else:
    return state.set(status='success')
