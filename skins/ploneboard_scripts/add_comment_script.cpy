## Controller Python Script "add_comment_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', text='', files=None
##title=Add a comment

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

pm = getToolByName(context, 'portal_membership')
wf = getToolByName(context, 'portal_workflow')

if pm.isAnonymousUser():
    creator = 'Anonymous'
else:
    creator = pm.getAuthenticatedMember().getUserName()

# Get files from session etc instead of just request
files = context.portal_ploneboard.getUploadedFiles()

new_context = context

if context.getTypeInfo().getId() == 'PloneboardComment':
    m = context.addReply(title=title, text=text, creator=creator, files=files)
    new_context = context.getConversation()        
elif context.getTypeInfo().getId() == 'PloneboardConversation':
    m = context.addComment(title=title, text=text, creator=creator, files=files)
else:
    return state.set(status='failure', portal_status_message='You can only add comments to conversations or comments.')

if m:
    context.portal_ploneboard.clearUploadedFiles()
    
    status = wf.getInfoFor(m, 'review_state')
    if status == 'pending':
        message = 'Comment is pending moderation'
    else:
        message = 'Comment added'    
    
    state.set(context=new_context, portal_status_message=message)

return state
