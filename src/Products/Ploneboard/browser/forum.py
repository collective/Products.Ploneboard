from DateTime import DateTime
from zope.interface import Interface, implements

from Products import Five
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.interfaces import IAboveContentTitle
from plone.app.layout.viewlets.common import ViewletBase

from Products.Ploneboard.batch import Batch
from Products.Ploneboard.browser.utils import toPloneboardTime, getNumberOfComments, getNumberOfConversations
from Products.Ploneboard.interfaces import IConversation, IComment


class IForumView(Interface):

    def getNumberOfConversations(self):
        """Returns the number of conversations in this forum."""


class ForumView(Five.BrowserView):
    """View methods for forum type
    """

    implements(IForumView)

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)
        self.catalog = getToolByName(context, 'portal_catalog')
        self.mt = getToolByName(context,'portal_membership')

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
        """Returns conversations."""
        catalog = self.catalog
        # We also have to look up member info and preferably cache that member info.

        res = []
        for conversation in \
                catalog(object_provides=IConversation.__identifier__,
                        sort_on='modified',
                        sort_order='reverse',
                        sort_limit=(offset+limit),
                        path='/'.join(self.context.getPhysicalPath()))[offset:offset+limit]:

            data = dict(review_state=conversation.review_state,
                        absolute_url=conversation.getURL(),
                        getNumberOfComments=conversation.num_comments,
                        modified=conversation.modified,
                        Title=conversation.Title,
                        Creator=conversation.Creator,
                        getLastCommentAuthor=None,# Depending on view rights to last comment
                        getLastCommentDate=None,
                        getLastCommentUrl=None,
                        )

            # Get last comment
            # THIS IS RATHER EXPENSIVE, AS WE DO CATALOG SEARCH FOR EVERY CONVERSATION
            # Investigate improved caching or something...
            tmp = self.catalog(
                object_provides=IComment.__identifier__,
                sort_on='created', sort_order='reverse', sort_limit=1,
                path=conversation.getPath())
            if tmp:
                lastcomment = tmp[0]
                data['getLastCommentUrl'] =       lastcomment.getURL()
                data['getLastCommentAuthor'] = lastcomment.Creator # Register member id for later lookup
                data['getLastCommentDate']   = self.toPloneboardTime(lastcomment.created)

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
        mt = getToolByName(self.context,'portal_membership')
        return mt.checkPermission('Ploneboard: Add Comment', self.context) \
          and mt.checkPermission('Add portal content', self.context)
