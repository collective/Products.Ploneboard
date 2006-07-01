## Controller Python Script "add_conversation_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title, text='', files=None
##title=Add a conversation

from Products.CMFCore.utils import getToolByName

pm = getToolByName(context, 'portal_membership')

if pm.isAnonymousUser():
    creator = 'Anonymous'
else:
    creator = pm.getAuthenticatedMember().getUserName()

# Get files from session etc instead of just request
files = context.portal_ploneboard.getUploadedFiles()

m = context.addConversation(title=title, text=text, creator=creator, files=files)

if m:
    context.portal_ploneboard.clearUploadedFiles()
    state.set(context=m.getForum(), portal_status_message='Added comment')

return state
