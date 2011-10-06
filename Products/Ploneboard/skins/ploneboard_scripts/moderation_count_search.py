## Script (Python) "list_pending_search.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=Searches for pending comments in moderated boards

if obj is None:
    obj = context

query = {}
query['review_state'] = 'pending'
query['portal_type'] = 'Ploneboard Comment'
query['path'] = '/'+ '/'.join(obj.getPhysicalPath()[1:])

reqget = context.REQUEST.get

# FIXME: this function seems useless
def supplement_query(field, index_name=None, reqget=reqget, query=query):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        query[index_name] = val

return len(context.getInternalCatalog()(REQUEST=query))
