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

    def searchMessages(query):
        """
        This method searches through all forums, conversations and messages.
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
        
    def getNumberOfMessages():
        """
        Returns the number of messages to this forum.
        """

class IConversation(Interface):
    """
    Conversation contains messages. The number of messages contained in 
    Conversation is high and increases. It is recommended to use BTree for
    indexing and to autogenerate ids for contained messages.
    """
    
    def getForum():
        """
        Returns the containing forum.
        """
        
    def addMessage(message_subject, message_body):
        """
        Adds a new message with subject and body.
        """
    
    def getMessage(message_id):
        """
        Returns the message with the specified id.
        """
    
    def getMessages(limit=30, offset=0, **kw):
        """
        Retrieves the specified number of messages with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        
    def getNumberOfmessages():
        """
        Returns the number of messages to this conversation.
        """

    def getLastMessageDate():
        """
        Returns a DateTime corresponding to the timestamp of the last message 
        for the conversation.
        """

class IMessage(Interface):
    """
    A message contains regular text body and metadata. It is folderish so it 
    can contain attachments.
    """
    
    def getConversation():
        """
        Returns the containing conversation.
        """
    
    def addReply(message_subject, message_body):
        """
        Add a response to this message.
        """
        
    def addAttachment(file):
        """
        Add a file attachment.
        """
        
    def hasAttachment():
        """
        Return 0 or 1 if this message has attachments.
        """

    def inReplyTo():
        """
        Returns the message object this message is a reply to. If it is the 
        topmost message (ie: first message in a conversation), it returns None.
        """

    def getReplies():
        """
        Returns the messages that were replies to this one.
        """
    
    def getSubject():
        """
        Returns the subject of the message.
        """
    
    def getBody():
        """
        Returns the body of the message.
        """
