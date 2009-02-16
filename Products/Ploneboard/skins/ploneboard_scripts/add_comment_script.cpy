## Controller Python Script "add_comment_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', text='', files=None
##title=Add a comment
# $Id$

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

new_context = context

if context.getTypeInfo().getId() == 'PloneboardComment':
    m = context.addReply(title=title, text=text, creator=creator, files=files)
    new_context = context.getConversation()
elif context.getTypeInfo().getId() == 'PloneboardConversation':
    m = context.addComment(title=title, text=text, creator=creator, files=files)
else:
    message = _(u"You can only add comments to conversations or comments.")
    putils.addPortalMessage(message)
    return state.set(status='failure')

if m:
    context.portal_ploneboard.clearUploadedFiles()

    status = wf.getInfoFor(m, 'review_state')
    if status == 'pending':
        message = _(u'Comment is pending moderation')
    else:
        message = _(u'Comment added')
    putils.addPortalMessage(message)
    state.set(context=new_context)

return state
