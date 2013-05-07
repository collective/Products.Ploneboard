## Script (Python) "comment_redirect_to_conversation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Redirect from a comment to it's conversation
##

# XXX if we ever do batching, we need extra logic here.
redirect_target = context.getConversation()
anchor = context.getId()
  
conv = context.getConversation()
query = {'object_implements' : 'Products.Ploneboard.interfaces.IComment',
         'sort_on'           : 'created',
         'path'              : '/'.join(conv.getPhysicalPath()),
        }
catalog=conv.getCatalog()
res = [ x.getId for x in catalog(query) ]
if anchor in res:
    pos = res.index(anchor)
    batchSize = conv.getForum().getConversationBatchSize()
    offset = batchSize * int(pos / batchSize)
else:
    offset = 0
target_url = '%s?b_start=%d#%s' % (redirect_target.absolute_url(), offset, anchor)
response = context.REQUEST.get('RESPONSE', None)
if response is not None:
    response.redirect(target_url)
    print "Redirecting to %s" % target_url
    return printed
