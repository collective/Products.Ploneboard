"""
$Id: Message.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
"""

import Globals

import random

from Acquisition import aq_base
from DateTime import DateTime
from OFS import Image

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFCore.PortalContent import PortalContent
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Referenceable import Referenceable

from BTrees.OIBTree import OIBTree
from BTrees.Length import Length
from Products.ZCatalog.Lazy import LazyMap

from PloneboardPermissions import ViewBoard, SearchBoard, ManageForum, \
     ManageBoard, AddMessage, AddMessageReply, EditMessage, AddAttachment, ManageMessage

from interfaces import IMessage
from Products.Archetypes.interfaces.referenceable import IReferenceable

factory_type_information = \
( { 'id'             : 'Ploneboard Message'
  , 'meta_type'      : 'Ploneboard Message'
  , 'description'    : """Message holds the message data and can contain attachments."""
  , 'icon'           : 'ploneboard_message_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'factory'        : None # To avoid it being visible in add contents menu
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

class Message(Referenceable, SkinnedFolder, PortalContent):
    """A message contains regular text body and metadata."""

    __implements__ = (IMessage, IReferenceable)

    meta_type = 'Ploneboard Message'
    manage_options = SkinnedFolder.manage_options
    
    security = ClassSecurityInfo()

    _replies = None       # OIBTree: { id -> 1 }
    _reply_count = None   # A BTrees.Length
    _in_reply_to = None   # Id to message this is a reply to

    def __init__(self, id, title='', text='', creator=None):
        self.id = id
        self.title = title
        self.text = text
        self.creation_date = DateTime()
        self._creator = creator
        self._attachments_ids = []

    security.declareProtected(ViewBoard, 'getConversation')
    def getConversation(self):
        """Returns the containing conversation."""
        return self.aq_inner.aq_parent
    
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
        message = Message(id, message_subject, message_body, creator)
        self.aq_inner.aq_parent._setObject(id, message)
        m = getattr(self.aq_inner.aq_parent, id)
        m._setPortalTypeName('Ploneboard Message')
        m.notifyWorkflowCreated()
        m.setInReplyTo(self)
        # Add to replies index
        self.setReply(m.getId())
        return m

    security.declareProtected(ViewBoard, 'inReplyTo')
    def inReplyTo(self):
        """
        Returns the message object this message is a reply to.
        """
        if not hasattr(self, '_in_reply_to'):
            self._in_reply_to = None
        return self.in_reply_to and self.aq_inner.aq_parent.getMessage(self._in_reply_to) or None

    
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
        if self.replies and self._replies.has_key(message_id):
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
        return self.text
    
    def childIds(self, level=0):
        """
        Returns list of ids of all child messages, excluding this message.
        """
        if level == 0:
            result = []
        else:
            result = [self.getId()]
        res = self.getResponses()
        if res:
            for msg_object in res:
                result = result + msg_object.childIds(level+1)
        return result
   
    
    security.declareProtected(ManageMessage, 'branch')
    def branch(self):
        """"""
        forum = self.getConversation().getForum()
        parent = self.getConversation()
        get_transaction().begin()
        conv = forum.addConversation(self.getSubject(), self.getBody())
        # here we get id of the first Message in newly created Conversation
        first_msg_id = conv.objectIds()[0]
        objects = [parent.getMessage(id) for id in self.childIds()]
        for obj in objects:
            obj_id = obj.getId()
            self_id = self.getId()
            conv._setObject(obj_id, obj)
            m = getattr(conv, obj_id)
            if m.inReplyTo() == self_id:
                m.setInReplyTo(first_msg_id)
            else:
                m.setInReplyTo(obj.inReplyTo())
        parent._delObject(self.getId()) # delete ourselves and all our descendants
        # if conversation after branching is empty, remove it
        if parent.getNumberOfMessages() == 0:
            forum._delObject(parent.getId())
        # we need to reindex stuff in newly created Conversation
        for o in conv.objectValues():
            o.reindexObject()
        get_transaction().commit()

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
        return getattr(self, '_creator', None) or SkinnedFolder.Creator(self)

    # Catalog related issues
    security.declareProtected(ViewBoard, 'indexObject')
    def indexObject(self):
        self._getBoardCatalog().indexObject(self)
        
    security.declareProtected(ViewBoard, 'unindexObject')
    def unindexObject(self):
        self._getBoardCatalog().unindexObject(self)
    
    security.declareProtected(ViewBoard, 'reindexObject')
    def reindexObject(self, idxs=[]):
        self._getBoardCatalog().reindexObject(self)
        
    def manage_afterAdd(self, item, container):
        """Add self to the conversation catalog."""
        Referenceable.manage_afterAdd(self, item, container)
        if aq_base(container) is not aq_base(self):
            self.indexObject()
            self.__recurse('manage_afterAdd', item, container)
        
    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item):
        Referenceable.manage_afterClone(self, item)
        PortalContent.manage_afterClone(self, item)

    def manage_beforeDelete(self, item, container):
        """Remove self from the conversation catalog."""
        Referenceable.manage_beforeDelete(self, item, container)
        if aq_base(container) is not aq_base(self):
            self.__recurse('manage_beforeDelete', item, container)
            self.unindexObject()
        # Remove from reply index
        self.inReplyTo().deleteReply(self.getId())

    def __recurse(self, name, *args):
        """ Recurse in subobjects. """
        values = self.objectValues()
        for ob in values:
            s = getattr(ob, '_p_changed', 0)
            if hasattr(aq_base(ob), name):
                getattr(ob, name)(*args)
            if s is None: ob._p_deactivate()

    def SearchableText(self):
        """ """
        return (self.title + ' ' + self.text)
    
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
    def listAttachments(self):
        """ """
        attachlist = []
        for attach_id in self._attachments_ids:
            attachlist.append(getattr(self, attach_id))
        return attachlist
    
    def getNumberOfAttachments(self):
        return len(self._attachments_ids)
    

def addMessage(self
              , id
              , title=''
              , description=''):
    """Factory method for creating message."""
    message = Message(id, title, description)
    self._setObject(id, message)

Globals.InitializeClass(Message)
