## Controller Python Script "add_conversation_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title, text='', creator=None, file=''
##title=Add a conversation

if not creator:
    creator = context.portal_membership.getAuthenticatedMember().getUserName()

m = context.addConversation(subject=title, body=text, creator=creator)
if m:
    state.set(context=m.getForum(), portal_status_message='Added comment')

return state
