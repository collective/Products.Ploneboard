import random
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DateTime import DateTime
from OFS import Image

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from Products.Ploneboard.config import PROJECTNAME

from BTrees.OIBTree import OIBTree
from BTrees.Length import Length
from Products.ZCatalog.Lazy import LazyMap

from Products.Ploneboard.PloneboardPermissions import ViewBoard, SearchBoard, ManageForum, \
     ManageBoard, AddConversation, AddComment, EditComment, AddAttachment, ManageComment

from Products.Ploneboard.interfaces import IComment

factory_type_information = \
( { 'id'             : 'PloneboardComment'
  , 'meta_type'      : 'PloneboardComment'
  , 'description'    : """Comments holds the comment data and can contain attachments."""
  , 'icon'           : 'ploneboard_comment_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'global_allow'   : 0 # To avoid it being visible in add contents menu
  , 'filter_content_types' : 1
  , 'allowed_content_types' : () 
  , 'immediate_view' : 'comment_edit_form'
  , 'aliases'        : {'(Default)':'comment_view',
                        'view':'comment_view'}
  , 'actions'        :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'string:${object_url}/comment_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'string:${object_url}/base_edit'
      , 'permissions'   : (ManageBoard,)
      , 'category'      : 'folder'
      }
    )
  },
)

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
              widget = TextAreaWidget(description = "Enter comment body.",
                                      description_msgid = "help_text",
                                      label = "Text",
                                      label_msgid = "label_text",
                                      rows = 5)),
    ))

class PloneboardComment(BaseBTreeFolder):
    """A comment contains regular text body and metadata."""

    __implements__ = (IComment,) + tuple(BaseBTreeFolder.__implements__)

    archetype_name = 'Comment'
    
    schema = schema
    
    _replies = None       # OIBTree: { id -> 1 }
    _reply_count = None   # A BTrees.Length
    _in_reply_to = None   # Id to comment this is a reply to

    security = ClassSecurityInfo()
    
    #def __init__(self, id, title='', text='', creator=None):
    #def __init__(self, oid, text='', creator=None, **kwargs):
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self.creation_date = DateTime()
        # Archetypes doesn't set values on creation from kwargs
        self._attachments_ids = []

    security.declareProtected(EditComment, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(AddComment, 'addReply')
    def addReply(self,
                 comment_subject,
                 comment_body,
                 creator=None ):
        """Add a reply to this comment."""
        if not self._replies or not self._reply_count:
            self._replies = OIBTree()
            self._reply_count = Length()

        min_id = int(self.id) + 1
        id = self.aq_inner.aq_parent.generateId(comment=1, min_id=min_id)
        if not comment_subject:
            comment_subject = self.aq_inner.aq_parent.Title()
        kwargs = {'title' : comment_subject, 
                  'creator' : creator,
                  'text' : comment_body
                  }
        #comment = PloneboardComment(id, comment_subject, comment_body, creator)
        comment = PloneboardComment(id)
        self.aq_inner.aq_parent._setObject(id, comment)
        m = getattr(self.aq_inner.aq_parent, id)
        m.initializeArchetype(**kwargs)
        m._setPortalTypeName('PloneboardComment')
        m.notifyWorkflowCreated()
        m.setInReplyTo(self)
        # Add to replies index
        self.setReply(m.getId())
        return m

    security.declareProtected(ViewBoard, 'inReplyTo')
    def inReplyTo(self):
        """
        Returns comment object this comment is a reply to.
        """
        if not hasattr(self, '_in_reply_to'):
            self._in_reply_to = None
        if self._in_reply_to:
            return self.aq_inner.aq_parent.getComment(self._in_reply_to)
        return self._in_reply_to # None
        #return self._in_reply_to and self.aq_inner.aq_parent.getComment(self._in_reply_to) or None

    
    security.declareProtected(AddComment, 'setReply')
    def setReply(self, comment_id):
        """ Updates the replies index """
        if not self._replies or not self._reply_count:
            self._replies = OIBTree()
            self._reply_count = Length()
        if not self._replies.has_key(comment_id):
            self._replies[comment_id] = 1
            self._reply_count.change(1)

    security.declareProtected(AddComment, 'deleteReply')
    def deleteReply(self, comment_id):
        """ Removes comment from the replies index """
        if self._replies and self._replies.has_key(comment_id):
            del self._replies[comment_id]
            self._reply_count.change(-1)

    security.declareProtected(AddComment, 'setInReplyTo')
    def setInReplyTo(self, comment_or_id):
        if type(comment_or_id) == type(''):
            self._in_reply_to = comment_or_id
        else:
            self._in_reply_to = comment_or_id.getId()

    security.declareProtected(ViewBoard, 'getReplies')
    def getReplies(self):
        """Returns the comments that were replies to this one."""
        if not self._replies or not self._reply_count:
            return []
        else:
            return LazyMap(self.aq_inner.aq_parent.getComment, self._replies.keys(), self._reply_count())
    
    security.declareProtected(ViewBoard, 'getSubject')
    def getSubject(self):
        """Returns the subject of the comment."""
        return self.Title()
    
    security.declareProtected(ViewBoard, 'getBody')
    def getBody(self):
        """Returns the body of the comment."""
        return self.getText()
    
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
        
        forum = self.getConversation().getForum()
        parent = self.getConversation()
        conv = forum.addConversation(self.getSubject(), self.getBody(), script=0)
        # here we get id of the first Comment in newly created Conversation
        first_msg_id = conv.objectIds()[0]

        ids.update({self.getId() : first_msg_id})
        
        objects = map(parent.getComment, self.childIds())
        for obj in objects:
            msg = conv.getComment(ids.get(obj.inReplyTo().getId())).addReply(obj.getSubject(), obj.getBody())
            ids.update({obj.getId() : msg.getId()})
            # Here we need to set some fields from old objects
            # What else should we update?
            msg.creation_date = obj.creation_date
            msg.setEffectiveDate(obj.EffectiveDate())
            msg.setExpirationDate(obj.ExpirationDate())
            msg.creator = obj.Creator()
        
        parent._delObject(self.getId(), recursive=1) # delete ourselves and all our descendants
        # if conversation after branching is empty, remove it
        if parent.getNumberOfComments() == 0:
            forum._delObject(parent.getId())
        # we need to reindex stuff in newly created Conversation
        #for o in conv.objectValues():
        #    o.reindexObject()

    # Workflow related methods - called by workflow scripts to control what to display
    def notifyPublished(self):
        """ Notify about publishing, so object can be added to index """
        self.aq_inner.aq_parent.setDateKey(self.id, self.creation_date or DateTime())
        self.aq_inner.aq_parent.notifyPublished()

    security.declareProtected(AddComment, 'notifyRetracted')
    def notifyRetracted(self):
        """ Notify about retracting, so object can be removed from index """
        self.aq_inner.aq_parent.delDateKey(self.id)
        if self.aq_inner.aq_parent.getNumberOfComments() == 0:
            self.aq_inner.aq_parent.notifyRetracted()

    security.declareProtected(ViewBoard, 'Creator')
    def Creator(self):
        return getattr(self, '_creator', None) or BaseBTreeFolder.Creator(self)

    # Catalog related issues
    security.declareProtected(ViewBoard, 'indexObject')
    def indexObject(self):
        BaseBTreeFolder.indexObject(self)
        self._getBoardCatalog().indexObject(self)
        
    security.declareProtected(ViewBoard, 'unindexObject')
    def unindexObject(self):
        self._getBoardCatalog().unindexObject(self)
        BaseBTreeFolder.unindexObject(self)
    
    security.declareProtected(ViewBoard, 'reindexObject')
    def reindexObject(self, idxs=[]):
        BaseBTreeFolder.reindexObject(self)
        self._getBoardCatalog().reindexObject(self)
        
    def manage_afterAdd(self, item, container):
        """Add self to the conversation catalog."""
        BaseBTreeFolder.manage_afterAdd(self, item, container)
        self.indexObject()
        
    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item):
        BaseBTreeFolder.manage_afterClone(self, item)
        self.reindexObject()

    def manage_beforeDelete(self, item, container):
        """Remove self from the conversation catalog."""
        # Remove from reply index
        #self.inReplyTo().deleteReply(self.getId())
        in_reply_to = self.inReplyTo()
        if in_reply_to is not None:
            in_reply_to.deleteReply(self.getId())
        BaseBTreeFolder.manage_beforeDelete(self, item, container)

    def SearchableText(self):
        """ """
        return (self.Title() + ' ' + self.getText())
    
    def _getBoardCatalog(self):
        return self.getConversation().getForum().getBoard().getInternalCatalog()

    ###########################
    # Attachment support      #
    ###########################
    security.declareProtected(ViewBoard, 'hasAttachment')
    def hasAttachment(self):
        """Return 0 or 1 if this comment has attachments."""
        if self._attachment_ids:
            return 1
        else:
            return 0

    security.declareProtected(AddAttachment, 'addAttachment')
    def addAttachment(self, title='', file=''):
        """ """
        if self.getNumberOfAttachments() < self.getConversation().getForum().getBoard().getNumberOfAttachments():
            id = "Attachment%08d" % (int(random.random() * 100000))
            while id in self._attachments_ids:
                id = "Attachment%08d" % (int(random.random() * 100000))
            attach = Image.File(id, title, file)
            self._setObject(id, attach)
            self._attachments_ids.append(id)
            self._p_checked = 1
    
    security.declareProtected(AddAttachment, 'removeAttachment')
    def removeAttachment(self, index=0):
        """ """
        if index > self.getNumberOfAttachments()-1:
            return
        id = self._attachments_ids[index]
        del self._attachments_ids[index]
        self._delObject(id)
        self._p_checked = 1
        
    security.declareProtected(AddAttachment, 'changeAttachment')
    def changeAttachment(self, index=0, title='', file=''):
        """ """
        attach = getattr(self, self._attachments_ids[index])
        if file:
            attach.manage_edit(title, '', filedata=file)
        else:
            # change title
            attach.manage_edit(title, '')
            
    security.declareProtected(AddAttachment, 'changeAttachmentTitle')
    def changeAttachmentTitle(self, index=0, title=''):
        """ """
        attach = getattr(self, self._attachments_ids[index])
        attach.manage_edit(title,'')
    
    security.declareProtected(AddAttachment, 'getAttachment')
    def getAttachment(self, index=0):
        """ """
        return getattr(self, self._attachments_ids[index])
    
    security.declareProtected(AddAttachment, 'getAttachments')
    def getAttachments(self):
        """ """
        return map(lambda id, this=self: getattr(this, id), self._attachments_ids)
    
    def getNumberOfAttachments(self):
        return len(self._attachments_ids)
    

    ############################################
    security.declareProtected(ViewBoard, 'getText')
    def getText(self, mimetype=None, **kwargs):
        """  """
        # Maybe we need to set caching for transform?
        
        orig = self.text.getRaw()
        
        pb_tool = getToolByName(self, 'portal_ploneboard')
        return pb_tool.performCommentTransform(orig, context=self)

    security.declareProtected(ViewBoard, 'Description')
    def Description(self, **kwargs):
        """We have to override Description here to handle arbitrary
        arguments since PortalFolder defines it."""
        if kwargs.get('mimetype', None) is None:
            kwargs['mimetype'] = 'text/plain'
        return self.getField('text').get(self, **kwargs)

    def __nonzero__(self):
        return 1

registerType(PloneboardComment, PROJECTNAME)
Globals.InitializeClass(PloneboardComment)

