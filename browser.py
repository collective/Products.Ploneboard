import urllib
from zope import interface
from Acquisition import aq_inner
from Products import Five
from Products.CMFCore import utils as cmf_utils
from Products.Ploneboard import permissions
from Products.Ploneboard.batch import Batch
from Products.Ploneboard.interfaces import IConversationView, ICommentView

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
                'creation_date': comment.CreationDate(),
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
        return info.get('fullname', creator)

    def quotedBody(self):
        text = self.context.getText()
        if text:
            return '<p>Previously %s wrote:</p>' \
                   '<blockquote>%s</blockquote><p></p>' % \
                   (self.author(), self.context.getText())
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
        batchSize = 30
        batchStart = int(self.request.get('b_start', 0))
        numComments = self.context.getNumberOfComments()
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

class RecentConversationsPortletView(Five.BrowserView):
    """Find recent conversations for portlet display
    """
    
    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)
        self.portal_workflow = cmf_utils.getToolByName(self.context, 'portal_workflow')
        self.plone_utils = cmf_utils.getToolByName(self.context, 'plone_utils')
    
    def results(self, sort_limit=5):
        catalog = cmf_utils.getToolByName(self.context, 'portal_catalog')
        results = catalog(object_implements='Products.Ploneboard.interfaces.IConversation', 
                            sort_on='modified', 
                            sort_order='reverse',
                            sort_limit=sort_limit)[:sort_limit]
        for r in results:
            yield self._buildDict(r.getObject())

    def _buildDict(self, ob):
        forum = ob.getForum()
        wfstate = self.portal_workflow.getInfoFor(ob, 'review_state')
        wfstate = self.plone_utils.normalizeString(wfstate)
        ptype = self.plone_utils.normalizeString(ob.getTypeInfo().getId())
        
        return { 'Title': ob.title_or_id(),
                 'Description' : ob.Description(),
                 'absolute_url': ob.absolute_url(),
                 'forum_title' : forum.title_or_id(),
                 'forum_url' : forum.absolute_url(),
                 'review_state_normalized' : wfstate,
                 'portal_type_normalized' : ptype,
               }

    
class RecentCommentsView(CommentViewableView):
    """Find recent comments
    """
    
class UnansweredCommentsView(CommentViewableView):
    """Find unanswered comments
    """

class DeleteCommentView(Five.BrowserView):
    """Delete the current comment.  If the comment is the root comment
    of a conversation, delete the entire conversation instead.
    """
    
    def __call__(self):
        redirect = self.request.response.redirect
        comment = self.context
        conversation = comment.getConversation()

        if len(conversation.getComments()) == 1:
            forum = conversation.getForum()
            conversation.delete()
            msg = urllib.quote('Conversation deleted')
            redirect(forum.absolute_url()+'?portal_status_message='+msg)
        else:
            comment.delete()
            msg = urllib.quote('Comment deleted')
            redirect(conversation.absolute_url()+'?portal_status_message='+msg)

