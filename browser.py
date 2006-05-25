from Products import Five
from Products.CMFCore import utils as cmf_utils
from Products.Ploneboard import permissions
from zope import interface

class CommentViewableView(Five.BrowserView):
    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

        self.portal_membership = cmf_utils.getToolByName(self.context, 
                                                         'portal_membership')

    def _buildDict(self, comment):
        return {
                'Title': comment.title_or_id(),
                'Creator': comment.Creator(),
                'creation_date': comment.creation_date,
                'getId': comment.getId(),
                'getText': comment.getText(),
                'absolute_url': comment.absolute_url(),
                'getAttachments': comment.getAttachments(),
                'canEdit': self._canEdit(comment),
                'getObject': comment,
            }

    def _canEdit(self, comment):
        checkPermission = self.context.portal_membership.checkPermission
        canEdit = checkPermission(permissions.EditComment, self.context)
        if not canEdit:
            return False
        
        for reply in comment.getReplies():
            reply_canEdit = self._canEdit(reply)
            if not reply_canEdit:
                return False

        return True

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
        for ob in self.context.getComments():
            yield self._buildDict(ob)
    
    def root_comments(self):
        for ob in self.context.getRootComments():
            yield self._buildDict(ob)

    def children(self, comment):
        if type(comment) is dict:
            comment = comment['getObject']
        
        for ob in comment.getReplies():
            yield self._buildDict(ob)       
