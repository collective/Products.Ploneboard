## Controller Python Script "add_message_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', text='', creator=None, file=''
##title=Add a message

if not creator:
    creator = context.portal_membership.getAuthenticatedMember().getUserName()

if context.getTypeInfo().getId() == 'PloneboardMessage':
    context.addReply(title, text, creator)
elif context.getTypeInfo().getId() == 'PloneboardConversation':
    context.addMessage(title, text, creator)
else:
    return state.set(status='failure', portal_status_message='You can only add messages to conversations or messages.')

return state