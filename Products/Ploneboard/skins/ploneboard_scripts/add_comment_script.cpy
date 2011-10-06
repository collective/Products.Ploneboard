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
from Products.Ploneboard.utils import PloneboardMessageFactory as _
from Products.CMFCore import permissions

pm = getToolByName(context, 'portal_membership')
wf = getToolByName(context, 'portal_workflow')
putils = getToolByName(context, 'plone_utils')

creator = str(pm.getAuthenticatedMember())

# Get files from session etc instead of just request
files = context.portal_ploneboard.getUploadedFiles()

new_context = context

ptype = context.portal_type
if ptype == 'PloneboardComment':
    m = context.addReply(title=title, text=text, creator=creator, files=files)
    new_context = context.getConversation()
elif ptype == 'PloneboardConversation':
    m = context.addComment(title=title, text=text, creator=creator, files=files)
else:
    message = _(u"You can only add comments to conversations or comments.")
    putils.addPortalMessage(message)
    return state.set(status='failure')

if m:
    if pm.checkPermission('Modify Portal Content', m):
        putils.acquireLocalRoles(m, 0)

    context.portal_ploneboard.clearUploadedFiles()
    new_context = m

    status = wf.getInfoFor(m, 'review_state')
    if status == 'pending':
        message = _(u'Comment is pending moderation')
    else:
        message = _(u'Comment added')
    putils.addPortalMessage(message)
    state.set(context=new_context)

return state
