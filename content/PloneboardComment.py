# zope3, zope 2.8, or Five dependency
from zope.interface import implements

from Products.Five.bridge import fromZ2Interface

import random
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_chain
from DateTime import DateTime
from OFS import Image
from OFS.Image import File

from BTrees.OIBTree import OIBTree
from BTrees.Length import Length
from Products.ZCatalog.Lazy import LazyMap

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField, ReferenceField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import RichWidget, ReferenceWidget
from Products.Archetypes.utils import shasattr

from Products.Ploneboard.config import PROJECTNAME, NUMBER_OF_ATTACHMENTS, PLONEBOARD_CATALOG, REPLY_RELATIONSHIP

from Products.CMFPlone.utils import _createObjectByType

from Products.Ploneboard.permissions import ViewBoard, SearchBoard, ManageForum, \
     ManageBoard, AddConversation, AddComment, EditComment, AddAttachment, ManageComment, \
     DeleteComment

from Products.Ploneboard.interfaces import IConversation, IComment

from Products.CMFPlone.interfaces.NonStructuralFolder \
    import INonStructuralFolder as ZopeTwoINonStructuralFolder
try:
    from Products.CMFPlone.interfaces.structure import INonStructuralFolder
except ImportError:
    INonStructuralFolder = fromZ2Interface(ZopeTwoINonStructuralFolder)

PBCommentBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBCommentBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBCommentBaseBTreeFolderSchema['title'].write_permission = AddComment


schema = PBCommentBaseBTreeFolderSchema + Schema((
    TextField('text',
              searchable = 1,
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              allowable_content_types=('text/html',
                                       'text/plain'),
              accessor='getText',
              read_permission = ViewBoard,
              write_permission = AddComment,
              widget = RichWidget(description = "Enter comment body.",
                                      description_msgid = "help_text",
                                      label = "Text",
                                      label_msgid = "label_text",
                                      rows = 5,
                                      helper_css = ('ploneboard.css',)
                                      )),
    ReferenceField(
        name='reply_to',
        accessor='inReplyTo', # Suboptimal accessor naming here...
        edit_accessor='inReplyToUID',
        mutator='setInReplyTo',
        relationship=REPLY_RELATIONSHIP,
        widget=ReferenceWidget(visible=False),
        ),
    ))

class PloneboardComment(BaseBTreeFolder):
    """A comment contains regular text body and metadata."""

    # Use RichDocument pattern for attachments
    # Don't inherit from btreefolder...

    implements(IComment, INonStructuralFolder)
    __implements__ = (BaseBTreeFolder.__implements__, ZopeTwoINonStructuralFolder)

    meta_type = 'PloneboardComment'
    archetype_name = 'Comment'

    schema = schema

    content_icon = 'ploneboard_comment_icon.gif'
    filter_content_types = 1
    allowed_content_types = ()
    global_allow = 0 # To avoid being visible in the add menu

    actions = (
            { 'id'          : 'view'
            , 'name'        : 'View'
            , 'action'      : 'string:$object_url'
            , 'permissions' : (ViewBoard,)
            },
        )

    aliases = \
        {
            '(Default)'               : 'comment_redirect_to_conversation'
            , 'view'                  : 'comment_redirect_to_conversation'
            , 'edit'                  : 'base_edit'
            , 'discussion_reply_form' : 'add_comment_form'
            , 'deleteDiscussion'      : 'retractComment'
        }

    _replies = None       # OIBTree: { id -> 1 }
    _reply_count = None   # A BTrees.Length
    _in_reply_to = None   # Id to comment this is a reply to

    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self.creation_date = DateTime()

    security.declareProtected(EditComment, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(ViewBoard, 'getConversation')
    def getConversation(self):
        """Returns containing conversation."""
        # Try containment
        stoptypes = ['Plone Site']
        for obj in aq_chain(aq_inner(self)):
            if hasattr(obj, 'portal_type') and obj.portal_type not in stoptypes:
                if IConversation.providedBy(obj):
                    return obj
        return None

    security.declareProtected(AddComment, 'addReply')
    def addReply(self,
                 title,
                 text,
                 creator=None,
                 files=None ):
        """Add a reply to this comment."""
        conv = self.getConversation()

        id = conv.generateId()
        if not title:
            title = conv.Title()
        kwargs = {'title' : title,
                  'creators' : [creator],
                  'text' : text,
                  'reply_to' : self.UID(),
                  }
        m = _createObjectByType(self.portal_type, conv, id, **kwargs)

        # Create files in message
        if files:
            for file in files:
                # Get raw filedata, not persistent object with reference to tempstorage
                # file.data might in fact be OFS.Image.Pdata - str will piece it all together
                attachment = File(file.getId(), file.title_or_id(), str(file.data), file.getContentType())
                m.addAttachment(attachment)

        conv.reindexObject() # Sets modified
        return m

    security.declareProtected(AddComment, 'deleteReply')
    def deleteReply(self, comment):
        """ Removes comment from the replies index """
        ### XXX THIS IS KINDA STUPID IF IT ONLY REMOVES THE RELATIONSHIP...
        comment.deleteReference(self, REPLY_RELATIONSHIP)

    security.declareProtected(ViewBoard, 'getReplies')
    def getReplies(self):
        """Returns the comments that were replies to this one."""
        # Return backreferences
        return self.getBRefs(REPLY_RELATIONSHIP)

    security.declareProtected(ViewBoard, 'getTitle')
    def getTitle(self):
        """Returns the subject of the comment."""
        return self.Title()

    def childIds(self, level=0):
        """
        Returns list of ids of all child comments, excluding this comment.
        """
        if level == 0:
            result = []
        else:
            result = [self.getId()]
        replies = self.getReplies()
        if replies:
            for msg_object in replies:
                result = result + msg_object.childIds(level+1)
        return result


    security.declareProtected(ManageComment, 'makeBranch')
    def makeBranch(self):
        """"""
        # Contains mappings - old_msg_id -> new_msg_id
        ids = {}

        parent = self.getConversation()
        forum = parent.getForum()
        conv = forum.addConversation(self.getTitle(), self.getText())
        # here we get id of the first Comment in newly created Conversation
        first_msg_id = conv.objectIds()[0]

        ids.update({self.getId() : first_msg_id})

        objects = map(parent.getComment, self.childIds())
        for obj in objects:
            replyId = obj.inReplyTo().getId()
            comment = conv.getComment(ids.get(replyId))
            msg = comment.addReply(obj.getTitle(), obj.getText())
            ids.update({obj.getId() : msg.getId()})
            # Here we need to set some fields from old objects
            # What else should we update?
            msg.creation_date = obj.creation_date
            msg.setEffectiveDate(obj.EffectiveDate())
            msg.setExpirationDate(obj.ExpirationDate())
            msg.creator = obj.Creator()

        # manually delete all replies
        for msgid in self.childIds():
            parent._delObject(msgid)
        parent._delObject(self.getId()) # delete ourselves and all our descendants
        # if conversation after branching is empty, remove it
        if parent.getNumberOfComments() == 0:
            forum._delObject(parent.getId())
        # we need to reindex stuff in newly created Conversation
        #for o in conv.objectValues():
        #    o.reindexObject()
        return conv

    ###########################
    # Attachment support      #
    # XXX use RichDocument pattern with NonStructuralFolder
    ###########################
    security.declareProtected(ViewBoard, 'hasAttachment')
    def hasAttachment(self):
        """Return 0 or 1 if this comment has attachments."""
        return not not self.objectIds(filter={'portal_type':['File', 'Image']})

    security.declareProtected(AddAttachment, 'addAttachment')
    def addAttachment(self, file, title=None):
        """ """
        if self.getNumberOfAttachments() < self.getNumberOfAllowedAttachments():
            content_type = file.getContentType()
            if content_type.startswith('image/'):
                type_name = 'Image'
                mutator = 'setImage'
            else:
                type_name = 'File'
                mutator = 'setFile'
            attachment = _createObjectByType(type_name, self, file.getId(),
                    title=file.title)
            getattr(attachment, mutator)(file)
            if title is not None:
                attachment.setTitle(title)
            attachment.unmarkCreationFlag()
            if shasattr(attachment, 'at_post_create_script'):
                attachment.at_post_create_script()

    security.declareProtected(AddAttachment, 'removeAttachment')
    def removeAttachment(self, id):
        """ """
        self._delObject(id)

    security.declareProtected(ViewBoard, 'getAttachment')
    def getAttachment(self, id):
        """ """
        return getattr(self, id)

    security.declareProtected(ViewBoard, 'getAttachments')
    def getAttachments(self):
        """ """
        return self.contentValues(filter={'portal_type':['File', 'Image']})

    security.declareProtected(ViewBoard, 'getNumberOfAttachments')
    def getNumberOfAttachments(self):
        return len(self.contentIds(filter={'portal_type':['File','Image']}))

    security.declareProtected(AddAttachment, 'getNumberOfAllowedAttachments')
    def getNumberOfAllowedAttachments(self):
        """
        Returns number of allowed attachments
        """
        return NUMBER_OF_ATTACHMENTS


    ############################################
    security.declareProtected(ViewBoard, 'getText')
    def getText(self, mimetype=None, **kwargs):
        """  """
        # Maybe we need to set caching for transform?

        orig = self.getRawText()

        pb_tool = getToolByName(self, 'portal_ploneboard')
        return pb_tool.performCommentTransform(orig, context=self)

    security.declareProtected(ViewBoard, 'Description')
    def Description(self, **kwargs):
        """We have to override Description here to handle arbitrary
        arguments since PortalFolder defines it."""
        if kwargs.get('mimetype', None) is None:
            kwargs['mimetype'] = 'text/plain'
        return self.getField('text').get(self, **kwargs)

    security.declareProtected(DeleteComment, "delete")
    def delete(self):
        """Delete this comment and make sure all comment replies to this
        comment are also cleaned up.
        """
        
        parent_comment = self.inReplyTo()
        for reply in self.getReplies():
            reply.setInReplyTo(parent_comment)
            reply.reindexObject()
        
        conversation = self.getConversation()
        conversation._delObject(self.getId())
        conversation.reindexObject()

    def __nonzero__(self):
        return 1
    
    def __str__(self):
        return "<PloneboardComment: title=%r;>" % self.Title()
    __repr__  = __str__

    
    security.declareProtected(DeleteComment, "object_delete")
    def object_delete(self):
        """Delete the comment the 'proper' way.
        """
        
        return self.restrictedTraverse('@@delete_view')()

registerType(PloneboardComment, PROJECTNAME)
