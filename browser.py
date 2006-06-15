import urllib
from zope import interface
from Products import Five
from Products.CMFCore import utils as cmf_utils
from Products.Ploneboard import permissions
from Products.Ploneboard.batch import Batch

class CommentViewableView(Five.BrowserView):
    """Any view that might want to interact with comments should inherit
    from this base class.
    """
    
    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

        self.portal_actions = cmf_utils.getToolByName(self.context,
                                                        'portal_actions')
        self.plone_utils = cmf_utils.getToolByName(self.context, 'plone_utils')
        self.portal_membership = cmf_utils.getToolByName(self.context, 
                                                         'portal_membership')

    def _buildDict(self, comment):
        """Produce a dict representative of all the important properties
        of a comment.
        """
        
        checkPermission = self.portal_membership.checkPermission
        actions = self.portal_actions.listFilteredActionsFor(comment)

        return {
                'Title': comment.title_or_id(),
                'Creator': comment.Creator(),
                'creation_date': comment.creation_date,
                'getId': comment.getId(),
                'getText': comment.getText(),
                'absolute_url': comment.absolute_url(),
                'getAttachments': comment.getAttachments(),
                'canEdit': checkPermission(permissions.EditComment, comment),
                'canDelete': checkPermission(permissions.DeleteComment, comment),
                'getObject': comment,
                'workflowActions' : actions['workflow'],
                'reviewStateTitle' :
			self.plone_utils.getReviewStateTitleFor(comment),
                'UID': comment.UID,
            }

class ICommentView(interface.Interface):
    def comment():
        """Return active comment.
        """
        
class CommentView(CommentViewableView):
    """A view for getting information about one specific comment.
    """
    
    interface.implements(ICommentView)
    
    def comment(self):
        return self._buildDict(self.context)


class IConversationView(interface.Interface):
    def comments():
        """Return all comments in the conversation.
        """
        
    def root_comments():
        """Return all of the root comments for a conversation.
        """
        
    def children(comment):
        """Return all of the children comments for a parent comment.
        """

class ConversationView(CommentView):
    """A view component for querying conversations.
    """
    
    interface.implements(IConversationView)

    def comments(self):
        batchSize = 30
        batchStart = int(self.request.get('b_start', 0))
        numComments = self.context.getNumberOfComments()
        return Batch(self._getComments, numComments, batchSize, batchStart, orphan=1)
        
        # XXX: This won't work, since the batch macros depend on the 'batch'
        # variable and its properties, not just the items its __getitem__
        # yields
        
        # for ob in batch:
        #    yield self._buildDict(ob)
    
    def root_comments(self):
        for ob in self.context.getRootComments():
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
