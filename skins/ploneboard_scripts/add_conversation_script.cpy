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

context.addConversation(title, text, creator)

return state
