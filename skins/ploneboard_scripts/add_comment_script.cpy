## Controller Python Script "add_comment_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', text='', creator=None, file=''
##title=Add a comment

if not creator:
    creator = context.portal_membership.getAuthenticatedMember().getUserName()

if context.getTypeInfo().getId() == 'PloneboardComment':
    m = context.addReply(comment_subject=title, comment_body=text, creator=creator)
elif context.getTypeInfo().getId() == 'PloneboardConversation':
    m = context.addComment(comment_subject=title, comment_body=text, creator=creator)
else:
    return state.set(status='failure', portal_status_message='You can only add comments to conversations or comments.')

if m:
    state.set(context=context.getConversation(), portal_status_message='Added comment')

return state