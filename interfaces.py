try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class IPloneboard(Interface):
    """
    Ploneboard is the outmost board object, what shows up in your site.
    The board contains forums. Board is folderish. The number of items contained
    in Board should be limited and steady.
    """
    
    def addForum(id, title, description):
        """
        The method add_forum takes id, title and description and creates a
        forum inside the board.
        """

    def getForums():
        """
        Return the forums
        """

    def removeForum(forum_id):
        """
        The method remove_forum removes the forum with the specified id from 
        this board.
        """

    def searchComments(query):
        """
        This method searches through all forums, conversations and comments.
        """

class IForum(Interface):
    """
    A Forum contains conversations. Forum is folderish. The number of items contained 
    in Forum is high and increases, so it is probably a good idea to use BTrees 
    for indexing. 
    """

    def getBoard():
        """
        Gets the containing board.
        """
        
    def addConversation(subject, body, **kw):
        """
        Adds a new conversation to the forum.
        """
        
    def getConversation(conversation_id):
        """
        Returns the conversation with the given conversation id.
        """
    
    def removeConversation(conversation_id):
        """
        Removes a conversation with the given conversation id from the forum.
        """
    
    def getConversations(limit=20, offset=0):
        """
        Returns a maximum of 'limit' conversations, the last updated conversations first, 
        starting from 'offset'.
        """

    def getNumberOfConversations():
        """
        Returns the number of conversations in this forum.
        """
        
    def getNumberOfComments():
        """
        Returns the number of comments to this forum.
        """

class IConversation(Interface):
    """
    Conversation contains comments. The number of comments contained in 
    Conversation is high and increases. It is recommended to use BTree for
    indexing and to autogenerate ids for contained comments.
    """
    
    def getForum():
        """
        Returns the containing forum.
        """
        
    def addComment(comment_subject, comment_body):
        """
        Adds a new comment with subject and body.
        """
    
    def getComment(comment_id):
        """
        Returns the comment with the specified id.
        """
    
    def getComments(limit=30, offset=0, **kw):
        """
        Retrieves the specified number of comments with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        
    def getNumberOfComments():
        """
        Returns the number of comments to this conversation.
        """

    def getLastCommentDate():
        """
        Returns a DateTime corresponding to the timestamp of the last comment 
        for the conversation.
        """

class IComment(Interface):
    """
    A comment contains regular text body and metadata. It is folderish so it 
    can contain attachments.
    """
    
    def getConversation():
        """
        Returns the containing conversation.
        """
    
    def addReply(comment_subject, comment_body):
        """
        Add a response to this comment.
        """
        
    def addAttachment(file):
        """
        Add a file attachment.
        """
        
    def hasAttachment():
        """
        Return 0 or 1 if this comment has attachments.
        """

    def inReplyTo():
        """
        Returns the comment object this comment is a reply to. If it is the 
        topmost comment (ie: first comment in a conversation), it returns None.
        """

    def getReplies():
        """
        Returns the comments that were replies to this one.
        """
    
    def getSubject():
        """
        Returns the subject of the comment.
        """
    
    def getBody():
        """
        Returns the body of the comment.
        """
