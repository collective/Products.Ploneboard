from DateTime import DateTime
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize
from Products import Five
from Products.Ploneboard.browser.utils import getNumberOfConversations
from Products.Ploneboard.browser.utils import toPloneboardTime
from Products.Ploneboard.interfaces import IConversation
from zope.interface import implementer

from .interfaces import IForumView


@implementer(IForumView)
class ForumView(Five.BrowserView):
    """View methods for forum type
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)
        self.catalog = api.portal.get_tool(name='portal_catalog')
        self.mt = api.portal.get_tool(name='portal_membership')

    @memoize
    def last_login(self):
        member = self.mt.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    @memoize
    def getNumberOfConversations(self):
        """Returns the number of conversations in this forum."""
        return getNumberOfConversations(self.context, self.catalog)

    def getConversations(self, limit=20, offset=0):
        """Returns conversations.
        """
        catalog = self.catalog
        res = []
        brains = catalog(
            object_provides=IConversation.__identifier__,
            sort_on='modified',
            sort_order='reverse',
            sort_limit=(offset + limit),
            path='/'.join(self.context.getPhysicalPath())
        )
        for brain in brains[offset:offset + limit]:
            data = dict()
            data['review_state'] = brain.review_state,
            data['absolute_url'] = brain.getURL()
            data['getNumberOfComments'] = brain.num_comments
            data['modified'] = brain.modified
            data['Title'] = brain.Title
            data['Creator'] = brain.Creator
            data['getLastCommentAuthor'] = brain.getLastCommentAuthor
            data['getLastCommentDate'] = self.toPloneboardTime(
                brain.getLastCommentDate
            )
            data['getLastCommentId'] = brain.getLastCommentId
            res.append(data)
        return res

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        return toPloneboardTime(self.context, self.request, time_)


class AddConversationViewlet(ViewletBase):

    @memoize
    def canStartConversation(self):
        """Check if user can start conversation
        """
        mt = api.portal.get_tool(name='portal_membership')
        has_add_conversation = mt.checkPermission(
            'Ploneboard: Add Conversation',
            self.context
        )
        has_add_portal_content = mt.checkPermission(
            'Add portal content',
            self.context
        )
        return has_add_conversation and has_add_portal_content