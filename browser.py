from Products import Five
from zope import interface
from Products.CMFCore import utils as cmf_utils

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

class ConversationView(Five.BrowserView):
    """A view component for querying conversations.
    """
    
    interface.implements(IConversationView)

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

        self.portal_membership = cmf_utils.getToolByName(self.context, 'portal_membership')
    
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

    def _buildDict(self, comment):
        checkPermission = self.context.portal_membership.checkPermission
        canEdit = checkPermission('Ploneboard: Edit Comment', self.context)
        
        return {
                'Title': comment.title_or_id(),
                'Creator': comment.Creator(),
                'creation_date': comment.creation_date,
                'getId': comment.getId(),
                'getText': comment.getText(),
                'absolute_url': comment.absolute_url(),
                'getAttachments': comment.getAttachments(),
                'canEdit': canEdit,
                'getObject': comment,
            }
