from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_chain
from DateTime import DateTime
from OFS.Image import File

from zope.interface import implements
from zope import event

from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField, ReferenceField
from Products.Archetypes.public import RichWidget, ReferenceWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard import utils
from Products.Ploneboard.config import PROJECTNAME, REPLY_RELATIONSHIP
from Products.Ploneboard.interfaces import IConversation, IComment
from Products.Ploneboard.permissions import AddAttachment
from Products.Ploneboard.permissions import AddComment
from Products.Ploneboard.permissions import DeleteComment
from Products.Ploneboard.permissions import EditComment
from Products.Ploneboard.permissions import ManageComment
from Products.Ploneboard.permissions import ViewBoard

PBCommentBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBCommentBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBCommentBaseBTreeFolderSchema['title'].write_permission = EditComment


schema = PBCommentBaseBTreeFolderSchema + Schema((
    TextField('text',
              searchable = 1,
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              allowable_content_types=('text/html',
                                       'text/plain'),
              accessor='getText',
              read_permission = ViewBoard,
              write_permission = EditComment,
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
utils.finalizeSchema(schema)


class PloneboardComment(BaseBTreeFolder):
    """A comment contains regular text body and metadata."""

    # Use RichDocument pattern for attachments
    # Don't inherit from btreefolder...

    implements(IComment, INonStructuralFolder)

    meta_type = 'PloneboardComment'

    schema = schema

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

        id = conv.generateId(prefix='')
        if not title:
            title = conv.Title()
            if not title.lower().startswith('re:'):
                title = 'Re: ' + title

        m = _createObjectByType(self.portal_type, conv, id)

        # XXX: There is some permission problem with AT write_permission
        # and using **kwargs in the _createObjectByType statement.
        m.setTitle(title)
        m.setText(text)
        m.setInReplyTo(self.UID())

        if creator is not None:
            m.setCreators([creator])

        # Create files in message
        if files:
            for file in files:
                # Get raw filedata, not persistent object with reference to tempstorage
                # file.data might in fact be OFS.Image.Pdata - str will piece it all together
                attachment = File(file.getId(), file.title_or_id(), str(file.data), file.getContentType())
                m.addAttachment(attachment)

        # If this comment is being added by anonymous, make sure that the true
        # owner in zope is the owner of the forum, not the parent comment or
        # conversation. Otherwise, that owner may be able to view or delete
        # the comment.
        membership = getToolByName(self, 'portal_membership')
        if membership.isAnonymousUser():
            forum = self.getConversation().getForum()
            utils.changeOwnershipOf(m, forum.owner_info()['id'], False)

        event.notify(ObjectInitializedEvent(m))
        m.reindexObject()
        conv.reindexObject() # Sets modified
        return m

    security.declareProtected(AddComment, 'deleteReply')
    def deleteReply(self, comment):
        """ Removes comment from the replies index """
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
    ###########################

    def attachmentFilter(self):
        return { 'portal_type' : [
                            'File', 'Image',
                            'ImageAttachment', 'FileAttachment'
                            ],
                }


    security.declareProtected(ViewBoard, 'hasAttachment')
    def hasAttachment(self):
        """Return 0 or 1 if this comment has attachments."""
        return not not self.objectIds(spec=self.attachmentFilter()['portal_type'])

    security.declareProtected(AddAttachment, 'validateAddAttachment')
    def validateAddAttachment(self, file):
        def FileSize(file):
            if hasattr(file, 'size'):
                size=file.size
            elif hasattr(file, 'tell'):
                file.seek(0, 2)
                size=file.tell()
                file.seek(0)
            else:
                try:
                    size=len(file)
                except TypeError:
                    size=0

            return size/1024

        if self.getNumberOfAttachments()>=self.getNumberOfAllowedAttachments():
            return False

        maxsize=self.getConversation().getMaxAttachmentSize()
        if maxsize!=-1:
            if FileSize(file)>maxsize:
                return False

        return True


    security.declareProtected(AddAttachment, 'addAttachment')
    def addAttachment(self, file, title=None):
        """ """
        if not self.validateAddAttachment(file):
            raise ValueError, "Attachment could not be added"

        content_type = file.getContentType()
        if content_type.startswith('image/'):
            type_name = 'ImageAttachment'
            mutator = 'setImage'
        else:
            type_name = 'FileAttachment'
            mutator = 'setFile'
        attachment = _createObjectByType(type_name, self, file.getId(),
                title=file.title)
        event.notify(ObjectInitializedEvent(attachment))

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
        return self.contentValues(filter=self.attachmentFilter())

    security.declareProtected(ViewBoard, 'getNumberOfAttachments')
    def getNumberOfAttachments(self):
        return len(self.contentIds(filter=self.attachmentFilter()))

    security.declareProtected(AddAttachment, 'getNumberOfAllowedAttachments')
    def getNumberOfAllowedAttachments(self):
        """
        Returns number of allowed attachments
        """
        parent = self.getConversation()
        forum = parent.getForum()
        return forum.getMaxAttachments()


    ############################################
    security.declareProtected(ViewBoard, 'getText')
    def getText(self, mimetype=None, **kwargs):
        """  """
        # Maybe we need to set caching for transform?


        unit=self.Schema()["text"].getBaseUnit(self)
        raw = unit.getRaw()
        content_type = unit.getContentType()

        pb_tool = getToolByName(self, 'portal_ploneboard')
        return pb_tool.performCommentTransform(raw, context=self,
                                               content_type=content_type)

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
