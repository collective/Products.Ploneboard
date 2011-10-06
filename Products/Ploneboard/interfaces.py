from zope.interface import Interface, Attribute


class IPloneboard(Interface):
    """
    Ploneboard is the outmost board object, what shows up in your site.
    The board contains forums. Board is folderish. The number of items contained
    in Board should be limited and steady.
    This is an optional type.
    """

    def addForum(id, title, description):
        """
        The method add_forum takes id, title and description and creates a
        forum inside the board.
        Should this go away and rather just use the regular Plone content
        creation? That would make it easier to switch content types.
        """

    def removeForum(forum_id):
        """
        The method remove_forum removes the forum with the specified id from
        this board.
        """

    def getForum(forum_id):
        """
        Return the forum for forum_id, or None.
        """

    def getForumIds():
        """
        Returns the ids of the forums.
        If this is the only board in a site, it should return forum ids for
        the entire site, not just inside the board.
        """

    def getForums():
        """
        Return the forums
        If this is the only board in a site, it should return forums for the
        entire site, not just inside the board.
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
        Returns None if there are no boards in the site.
        """

    def addConversation(subject, body, **kw):
        """
        Adds a new conversation to the forum.
        Should this go away and rather just use the regular Plone content
        creation? That would make it easier to switch content types.
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

    def getLastCommentAuthor():
        """
        Returns the author of the last comment for the conversation.
        """

    def getLastComment():
        """
        Returns the last comment as full object (no Brain).
        If there is no such one then None is returned
        """

    def getRootComments():
        """
        Return a list all comments rooted to the board; ie comments which
        are not replies to other comments.
        """

    def getFirstComment():
        """
        Returns the first (aka root) comment in this IConversation.
        """


class IComment(Interface):
    """
    A comment contains regular text body and metadata.
    """

    def getConversation():
        """
        Returns the containing conversation.
        """

    def addReply(comment_subject, comment_body):
        """
        Add a response to this comment of same type as object itself.
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

    def getTitle():
        """
        Returns the title of the comment.
        """

    def getText():
        """
        Returns the text of the comment.
        """

    def delete():
        """
        Delete this comment.  Will ensure to clean up any comments
        that were replies to this comment.
        """

class IAttachmentSupport(Interface):
    """
    Attachment support, typically for comments
    """
    def addAttachment(file, title=None):
        """
        Add a file attachment.
        """

    def hasAttachment():
        """
        Return 0 or 1 if this comment has attachments.
        """

    def getNumberOfAllowedAttachments():
        """
        Return the number of allowed attachments
        """

    def getNumberOfAttachments():
        """
        Return the number of attachments
        """
    def getAttachments():
        """
        Return all attachments
        """

class IPloneboardTool(Interface):
    """Services for Ploneboard: Handles text transformation plugins and attached files.
    """

    id = Attribute('id', 'Must be set to "portal_ploneboard"')

    def registerTransform(name, module, friendlyName=None):
        """Adds a text transformation module to portal_transforms.
        Used from the configuration panel
        """

    def unregisterTransform(name):
        """Removes the transformation module from portal_transforms
        Used from the configuration panel
        """

    def enableTransform(name, enabled=True):
        """Globally enables a transform (site wide)
        """

    def unregisterAllTransforms():
        """Removes from portal_transforms all transform modules added with Ploneboard
        """

    def getTransforms():
        """Returns list of transform names.
        """

    def getTransformFriendlyName(name):
        """Returns a friendly name for the given transform.
        """

    def getEnabledTransforms():
        """Returns list of names for enabled transforms.
        """

    def performCommentTransform(orig, **kwargs):
        """This performs the comment transform - also used for preview.
        """

    def getUploadedFiles():
        """Stores files from request in session and returns these files
        """

    def clearUploadedFiles():
        """Removes uploaded files from session machinery
        """
