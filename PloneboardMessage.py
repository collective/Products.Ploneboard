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
from config import PROJECTNAME

from BTrees.OIBTree import OIBTree
from BTrees.Length import Length
from Products.ZCatalog.Lazy import LazyMap

from PloneboardPermissions import ViewBoard, SearchBoard, ManageForum, \
     ManageBoard, AddMessage, AddMessageReply, EditMessage, AddAttachment, ManageMessage

from interfaces import IMessage

factory_type_information = \
( { 'id'             : 'PloneboardMessage'
  , 'meta_type'      : 'PloneboardMessage'
  , 'description'    : """Message holds the message data and can contain attachments."""
  , 'icon'           : 'ploneboard_message_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'global_allow'   : 0 # To avoid it being visible in add contents menu
  , 'filter_content_types' : 1
  , 'allowed_content_types' : () 
  , 'immediate_view' : 'message_edit_form'
  , 'aliases'        : {'(Default)':'message_view',
                        'view':'message_view'}
  , 'actions'        :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'string:${object_url}/message_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'string:${object_url}/message_edit_form'
      , 'permissions'   : (ManageBoard,)
      , 'category'      : 'folder'
      }
    )
  },
)

schema = BaseBTreeFolderSchema + Schema((
    TextField('text',
              searchable = 1,
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              allowable_content_types=('text/html',
                                       'text/plain'),
              accessor='getText',  
              widget = TextAreaWidget(description = "Enter message body.",
                                      description_msgid = "help_text",
                                      label = "Text",
                                      label_msgid = "label_text",
                                      rows = 5)),
    ))

class PloneboardMessage(BaseBTreeFolder):
    """A message contains regular text body and metadata."""

    __implements__ = (IMessage,) + tuple(BaseBTreeFolder.__implements__)

    archetype_name = 'Ploneboard Message'
    
    schema = schema
    
    _replies = None       # OIBTree: { id -> 1 }
    _reply_count = None   # A BTrees.Length
    _in_reply_to = None   # Id to message this is a reply to

    security = ClassSecurityInfo()
    
    #def __init__(self, id, title='', text='', creator=None):
    #def __init__(self, oid, text='', creator=None, **kwargs):
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self.creation_date = DateTime()
        # Archetypes doesn't set values on creation from kwargs
        self.setTitle(kwargs.get('title', ''))
        self._creator = kwargs.get('creator', '')
        self.setText(kwargs.get('text', ''))
        self._attachments_ids = []

    security.declareProtected(AddMessageReply, 'addReply')
    def addReply(self,
                 message_subject,
                 message_body,
                 creator=None ):
        """Add a reply to this message."""
        if not self._replies or not self._reply_count:
            self._replies = OIBTree()
            self._reply_count = Length()

        min_id = int(self.id) + 1
        id = self.aq_inner.aq_parent.generateId(message=1, min_id=min_id)
        if not message_subject:
            message_subject = self.aq_inner.aq_parent.Title()
        kwargs = {'title' : message_subject, 
                  'creator' : creator,
                  'text' : message_body
                  }
        #message = PloneboardMessage(id, message_subject, message_body, creator)
        message = PloneboardMessage(id, **kwargs)
        self.aq_inner.aq_parent._setObject(id, message)
        m = getattr(self.aq_inner.aq_parent, id)
        m._setPortalTypeName('PloneboardMessage')
        m.notifyWorkflowCreated()
        m.setInReplyTo(self)
        # Add to replies index
        self.setReply(m.getId())
        return m

    security.declareProtected(ViewBoard, 'inReplyTo')
    def inReplyTo(self):
        """
        Returns message object this message is a reply to.
        """
        if not hasattr(self, '_in_reply_to'):
            self._in_reply_to = None
        if self._in_reply_to:
            return self.aq_inner.aq_parent.getMessage(self._in_reply_to)
        return self._in_reply_to # None
        #return self._in_reply_to and self.aq_inner.aq_parent.getMessage(self._in_reply_to) or None

    
    security.declareProtected(AddMessageReply, 'setReply')
    def setReply(self, message_id):
        """ Updates the replies index """
        if not self._replies or not self._reply_count:
            self._replies = OIBTree()
            self._reply_count = Length()
        if not self._replies.has_key(message_id):
            self._replies[message_id] = 1
            self._reply_count.change(1)

    security.declareProtected(AddMessageReply, 'deleteReply')
    def deleteReply(self, message_id):
        """ Removes message from the replies index """
        if self._replies and self._replies.has_key(message_id):
            del self._replies[message_id]
            self._reply_count.change(-1)

    security.declareProtected(AddMessageReply, 'setInReplyTo')
    def setInReplyTo(self, message_or_id):
        if type(message_or_id) == type(''):
            self._in_reply_to = message_or_id
        else:
            self._in_reply_to = message_or_id.getId()

    security.declareProtected(ViewBoard, 'getReplies')
    def getReplies(self):
        """Returns the messages that were replies to this one."""
        if not self._replies or not self._reply_count:
            return []
        else:
            return LazyMap(self.aq_inner.aq_parent.getMessage, self._replies.keys(), self._reply_count())
    
    security.declareProtected(ViewBoard, 'getSubject')
    def getSubject(self):
        """Returns the subject of the message."""
        return self.Title()
    
    security.declareProtected(ViewBoard, 'getBody')
    def getBody(self):
        """Returns the body of the message."""
        return self.getText()
    
    def childIds(self, level=0):
        """
        Returns list of ids of all child messages, excluding this message.
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
   
    
    security.declareProtected(ManageMessage, 'makeBranch')
    def makeBranch(self):
        """"""
        # Contains mappings - old_msg_id -> new_msg_id
        ids = {}
        
        forum = self.getConversation().getForum()
        parent = self.getConversation()
        conv = forum.addConversation(self.getSubject(), self.getBody(), script=0)
        # here we get id of the first Message in newly created Conversation
        first_msg_id = conv.objectIds()[0]

        ids.update({self.getId() : first_msg_id})
        
        objects = map(parent.getMessage, self.childIds())
        for obj in objects:
            msg = conv.getMessage(ids.get(obj.inReplyTo().getId())).addReply(obj.getSubject(), obj.getBody())
            ids.update({obj.getId() : msg.getId()})
            # Here we need to set some fields from old objects
            # What else should we update?
            msg.creation_date = obj.creation_date
            msg.setEffectiveDate(obj.EffectiveDate())
            msg.setExpirationDate(obj.ExpirationDate())
            msg.creator = obj.Creator()
        
        parent._delObject(self.getId(), recursive=1) # delete ourselves and all our descendants
        # if conversation after branching is empty, remove it
        if parent.getNumberOfMessages() == 0:
            forum._delObject(parent.getId())
        # we need to reindex stuff in newly created Conversation
        #for o in conv.objectValues():
        #    o.reindexObject()

    # Workflow related methods - called by workflow scripts to control what to display
    def notifyPublished(self):
        """ Notify about publishing, so object can be added to index """
        self.aq_inner.aq_parent.setDateKey(self.id, self.creation_date or DateTime())
        self.aq_inner.aq_parent.notifyPublished()

    security.declareProtected(AddMessage, 'notifyRetracted')
    def notifyRetracted(self):
        """ Notify about retracting, so object can be removed from index """
        self.aq_inner.aq_parent.delDateKey(self.id)
        if self.aq_inner.aq_parent.getNumberOfMessages() == 0:
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
        """Return 0 or 1 if this message has attachments."""
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
    
    security.declareProtected(AddAttachment, 'listAttachments')
    def getAttachments(self):
        """ """
        return map(lambda id, this=self: getattr(this, id), self._attachments_ids)
    
    def getNumberOfAttachments(self):
        return len(self._attachments_ids)
    

    ############################################
    def getText(self, mimetype=None, **kwargs):
        """  """
        # Maybe we need to set cashing for transform?
        
        orig = self.text.getRaw()
        
        pb_tool = getToolByName(self, 'portal_ploneboard')
        transform_tool = getToolByName(self, 'portal_transforms')
        
        # This one is very important, because transform object has no 
        # acquisition context inside it, so we need to pass it our one
        kwargs.update({ 'context' : self })
        
        data = transform_tool._wrap('text/plain')
        
        for transform in map(lambda x: x[1], pb_tool.getEnabledTransforms()):
            data = transform.convert(orig, data, **kwargs)
            orig = data.getData()
            transform_tool._setMetaData(data, transform)
        
        orig = orig.replace('\n', '<br/>')
        return orig

    def __nonzero__(self):
        return 1

registerType(PloneboardMessage, PROJECTNAME)
Globals.InitializeClass(PloneboardMessage)

