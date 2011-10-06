from zope import interface
from Acquisition import aq_base
from DateTime.DateTime import DateTime
from Products import Five
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.utils import getToolByName
from Products.Ploneboard import permissions
from Products.Ploneboard.batch import Batch
from Products.Ploneboard.browser.interfaces import IConversationView
from Products.Ploneboard.browser.interfaces import ICommentView
from Products.Ploneboard.browser.utils import toPloneboardTime
from Products.Ploneboard.utils import PloneboardMessageFactory as _


class CommentViewableView(Five.BrowserView):
    """Any view that might want to interact with comments should inherit
    from this base class.
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

        self.portal_actions = cmf_utils.getToolByName(self.context, 'portal_actions')
        self.plone_utils = cmf_utils.getToolByName(self.context, 'plone_utils')
        self.portal_membership = cmf_utils.getToolByName(self.context, 'portal_membership')
        self.portal_workflow = cmf_utils.getToolByName(self.context, 'portal_workflow')

    def _buildDict(self, comment):
        """Produce a dict representative of all the important properties
        of a comment.
        """

        checkPermission = self.portal_membership.checkPermission
        actions = self.portal_actions.listFilteredActionsFor(comment)

        res= {
                'Title': comment.title_or_id(),
                'Creator': comment.Creator(),
                'creation_date': self.toPloneboardTime(comment.CreationDate()),
                'getId': comment.getId(),
                'getText': comment.getText(),
                'absolute_url': comment.absolute_url(),
                'getAttachments': comment.getAttachments(),
                'canEdit': checkPermission(permissions.EditComment, comment),
                'canDelete': checkPermission(permissions.DeleteComment, comment),
                'canReply': checkPermission(permissions.AddComment, comment),
                'getObject': comment,
                'workflowActions' : actions['workflow'],
                'review_state' : self.portal_workflow.getInfoFor(comment, 'review_state'),
                'reviewStateTitle' : self.plone_utils.getReviewStateTitleFor(comment),
                'UID': comment.UID(),
            }
        return res

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        return toPloneboardTime(self.context, self.request, time_)


class CommentView(CommentViewableView):
    """A view for getting information about one specific comment.
    """

    interface.implements(ICommentView)

    def comment(self):
        return self._buildDict(self.context)

    def author(self):
        creator = self.context.Creator()
        info = self.portal_membership.getMemberInfo(creator)
        if info is None:
            return creator
        fullname_or_id = info.get('fullname') or info.get('username') or creator
        return fullname_or_id

    def quotedBody(self):
        text = self.context.getText()
        if text:
            try:
                return _("label_quote", u"Previously ${author} wrote: ${quote}", {"author": unicode(self.author(), 'utf-8'),
                    "quote":  unicode("<blockquote>%s</blockquote></br>" % (self.context.getText()), 'utf-8')})
            except TypeError:
                return _("label_quote", u"Previously ${author} wrote: ${quote}", {"author": self.author(), 
                    "quote":  unicode("<blockquote>%s</blockquote></br>" % (self.context.getText()), 'utf-8')})            
        else:
            return ''

class ConversationView(CommentView):
    """A view component for querying conversations.
    """

    interface.implements(IConversationView)

    def conversation(self):
        checkPermission = self.portal_membership.checkPermission
        conv = self.context
        forum = conv.getForum()

        return {
                'maximumAttachments' : forum.getMaxAttachments(),
                'maximumAttachmentSize' : forum.getMaxAttachmentSize(),
                'canAttach': forum.getMaxAttachments()>0 and \
                              checkPermission(permissions.AddAttachment,conv),
                }

    def comments(self):
        conv = self.context
        forum = conv.getForum()
        batchSize = forum.getConversationBatchSize()
        batchStart = int(self.request.get('b_start', 0))
        if type(batchStart) == type('a'):
            batchStart = int(batchStart.split('#')[0])
        numComments = conv.getNumberOfComments()
        return Batch(self._getComments, numComments, batchSize, batchStart, orphan=1)

    def root_comments(self):
        rootcomments =  self.context.getRootComments()
        for ob in rootcomments:
            yield self._buildDict(ob)

    def children(self, comment):
        if type(comment) is dict:
            comment = comment['getObject']

        for ob in comment.getReplies():
            yield self._buildDict(ob)

    def _getComments(self, limit, offset):
        """Dictify comments before returning them to the batch
        """
        return [self._buildDict(ob) for ob in self.context.getComments(limit=limit, offset=offset)]


class RecentConversationsView(CommentViewableView):
    """Find recent conversations
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)
        self.portal_workflow = cmf_utils.getToolByName(self.context, 'portal_workflow')
        self.plone_utils = cmf_utils.getToolByName(self.context, 'plone_utils')
        self.portal_catalog = cmf_utils.getToolByName(self.context, 'portal_catalog')
        self.portal_membership = cmf_utils.getToolByName(self.context, 'portal_membership')

    def num_conversations(self):
        catalog = self.portal_catalog
        results = catalog(object_provides='Products.Ploneboard.interfaces.IConversation',
                          path='/'.join(self.context.getPhysicalPath()),)
        return len(results)

    def results(self, limit=20, offset=0):
        catalog = self.portal_catalog
        results = catalog(object_provides='Products.Ploneboard.interfaces.IConversation',
                            sort_on='modified',
                            sort_order='reverse',
                            sort_limit=(offset+limit),
                            path='/'.join(self.context.getPhysicalPath()))[offset:offset+limit]
        return filter(None, [self._buildDict(r.getObject()) for r in results])

    def _buildDict(self, ob):
        forum = ob.getForum()
        wfstate = self.portal_workflow.getInfoFor(ob, 'review_state')
        wfstate = self.plone_utils.normalizeString(wfstate)

        creator = ob.Creator()
        creatorInfo = self.portal_membership.getMemberInfo(creator)
        if creatorInfo is not None and creatorInfo.get('fullname', "") != "":
            creator = creatorInfo['fullname']

        lastComment = ob.getLastComment()
        if lastComment is None:
            return None
        canAccessLastComment = self.portal_membership.checkPermission('View', lastComment)

        lastCommentCreator = lastComment.Creator()
        creatorInfo = self.portal_membership.getMemberInfo(lastCommentCreator)
        if creatorInfo is not None and creatorInfo.get('fullname', '') != "":
            lastCommentCreator = creatorInfo['fullname']

        return { 'Title': ob.title_or_id(),
                 'Description' : ob.Description(),
                 'absolute_url': ob.absolute_url(),
                 'forum_title' : forum.title_or_id(),
                 'forum_url' : forum.absolute_url(),
                 'review_state_normalized' : wfstate,
                 'num_comments' : ob.getNumberOfComments(),
                 'creator' : creator,
                 'last_comment_id' : lastComment.getId(),
                 'last_comment_creator' : lastCommentCreator,
                 'last_comment_date' : lastComment.created(),
                 'can_access_last_comment' : canAccessLastComment,
                 'is_new' : self._is_new(ob.modified()),
               }

    def _is_new(self, modified):
        llt = getattr(aq_base(self), '_last_login_time', [])
        if llt == []:
            m = self.portal_membership.getAuthenticatedMember()
            if m.has_role('Anonymous'):
                llt = self._last_login_time = None
            else:
                llt = self._last_login_time = m.getProperty('last_login_time', 0)
        if llt is None: # not logged in
            return False
        elif llt == 0: # never logged in before
            return True
        else:
            return (modified >= DateTime(llt))

class UnansweredConversationsView(RecentConversationsView):
    """Find unanswered conversations
    """

    def num_conversations(self):
        catalog = self.portal_catalog
        results = catalog(object_provides='Products.Ploneboard.interfaces.IConversation',
                          num_comments=1,
                          path='/'.join(self.context.getPhysicalPath()),)
        return len(results)

    def results(self, limit=20, offset=0):
        catalog = self.portal_catalog
        results = catalog(object_provides='Products.Ploneboard.interfaces.IConversation',
                            num_comments=1,
                            sort_on='modified',
                            sort_order='reverse',
                            sort_limit=(offset+limit),
                            path='/'.join(self.context.getPhysicalPath()))[offset:offset+limit]
        return [self._buildDict(r.getObject()) for r in results]

    def _buildDict(self, ob):
        forum = ob.getForum()
        wfstate = self.portal_workflow.getInfoFor(ob, 'review_state')
        wfstate = self.plone_utils.normalizeString(wfstate)

        creator = ob.Creator()
        creatorInfo = self.portal_membership.getMemberInfo(creator)
        if creatorInfo is not None and creatorInfo.get('fullname', "") != "":
            creator = creatorInfo['fullname']

        return { 'Title': ob.title_or_id(),
                 'Description' : ob.Description(),
                 'created' : ob.created(),
                 'absolute_url': ob.absolute_url(),
                 'forum_title' : forum.title_or_id(),
                 'forum_url' : forum.absolute_url(),
                 'review_state_normalized' : wfstate,
                 'creator' : creator,
                 'is_new' : self._is_new(ob.modified()),
               }

class DeleteCommentView(Five.BrowserView):
    """Delete the current comment.  If the comment is the root comment
    of a conversation, delete the entire conversation instead.
    """

    def __call__(self):
        redirect = self.request.response.redirect
        comment = self.context
        conversation = comment.getConversation()
        plone_utils = cmf_utils.getToolByName(comment, 'plone_utils')

        if len(conversation.getComments()) == 1:
            forum = conversation.getForum()
            conversation.delete()
            msg = _(u'Conversation deleted')
            plone_utils.addPortalMessage(msg)
            redirect(forum.absolute_url())
        else:
            comment.delete()
            msg = _(u'Comment deleted')
            plone_utils.addPortalMessage(msg)
            redirect(conversation.absolute_url())

