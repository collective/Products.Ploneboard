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
view = redirect_target.restrictedTraverse("@@plone_context_state").view_url()
anchor = context.getId()
  
response = context.REQUEST.get('RESPONSE', None)
if response is not None:
    response.redirect('%s#%s' % (view, anchor))
    print "Redirecting to %s" % redirect_target.absolute_url()
    return printed
    
