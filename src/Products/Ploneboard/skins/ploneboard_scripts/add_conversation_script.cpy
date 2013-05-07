## Controller Python Script "add_conversation_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title, text='', files=None
##title=Add a conversation

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.utils import PloneboardMessageFactory as _

pm = getToolByName(context, 'portal_membership')
wf = getToolByName(context, 'portal_workflow')
putils = getToolByName(context, 'plone_utils')

if pm.isAnonymousUser():
    creator = 'Anonymous'
else:
    creator = pm.getAuthenticatedMember().getId()

# Get files from session etc instead of just request
files = context.portal_ploneboard.getUploadedFiles()

m = context.addConversation(title=title, text=text, creator=creator, files=files)

if m:
    context.portal_ploneboard.clearUploadedFiles()
    try:
        new_context = m.getForum()
    except Unauthorized:
        # If we are unable to view the new comment (e.g. because it is pending
        # and user is anonymous, rely on old context)
        new_context = context

    status = wf.getInfoFor(m, 'review_state')
    if status == 'pending':
        message = _(u'Conversation is pending moderation')
    else:
        message = _(u'Conversation added')

    putils.addPortalMessage(message)
    state.set(context=new_context)

return state
