"""
$Id: Conversation.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
"""

from random import randint

import Globals

from Acquisition import aq_base
from DateTime import DateTime

from Products.ZCatalog.Lazy import LazyMap

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFCore.PortalContent import PortalContent
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Referenceable import Referenceable

from PloneboardPermissions import ViewBoard, SearchBoard, ManageForum, ManageBoard, AddMessage, AddMessageReply, ManageConversation
from Message import Message
from PloneboardIndex import PloneboardIndex
from interfaces import IConversation, IMessage
from Products.Archetypes.interfaces.referenceable import IReferenceable

factory_type_information = \
( { 'id'             : 'Ploneboard Conversation'
  , 'meta_type'      : 'Ploneboard Conversation'
  , 'description'    : """Conversations hold messages."""
  , 'icon'           : 'ploneboard_conversation_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'factory'        : None # To avoid it being visible in add contents menu
  , 'filter_content_types' : 1
  , 'allowed_content_types' : ('Ploneboard Message', ) 
  , 'immediate_view' : 'conversation_edit_form'
  , 'aliases'        : {'(Default)':'conversation_view',
                        'view':'conversation_view'}
  , 'actions'        :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'string:${object_url}/conversation_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'string:${object_url}/conversation_edit_form'
      , 'permissions'   : (ManageBoard,)
      , 'category'      : 'folder'
      }
    )
  },
)

class ConversationIndex(PloneboardIndex):
    """
    A class for containing the date indexes and handling length (map to __len__)
    """
    def _calculateInternalDateKey(self, date):
        # Date key as int
        return int(date)


MAX_UNIQUEID_ATTEMPTS = 1000

class Conversation(Referenceable, BTreeFolder2Base, SkinnedFolder, PortalContent):
    """
    Conversation contains messages.
    """

    __implements__ = (IConversation, IReferenceable)

    meta_type = 'Ploneboard Conversation'
    manage_options = SkinnedFolder.manage_options
    
    security = ClassSecurityInfo()

    _index = None

    def __init__(self, id, title='', creator=None):
        SkinnedFolder.__init__(self, id, title)
        BTreeFolder2Base.__init__(self, id)
        self._index = ConversationIndex()
        self._creator = creator

    security.declareProtected(ViewBoard, 'getForum')
    def getForum(self):
        """Returns the containing forum."""
        return self.aq_inner.aq_parent

    security.declareProtected(AddMessage, 'addMessage')
    def addMessage( self, message_subject, message_body, creator=None ):
        """Adds a new message with subject and body."""
        id = self.generateId(message=1)
        if not message_subject:
            message_subject = self.Title()
        message = Message(id, message_subject, message_body, creator)
        self._setObject(id, message)
        m = getattr(self, id)
        m._setPortalTypeName('Ploneboard Message')
        m.notifyWorkflowCreated()
        return m
    
    security.declareProtected(ViewBoard, 'getMessage')
    def getMessage(self, message_id, default=None):
        """Returns the message with the specified id."""
        return self._getOb(message_id, default)
    
    security.declareProtected(ViewBoard, 'getMessages')
    def getMessages(self, limit=30, offset=0, **kw):
        """
        Retrieves the specified number of messages with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        keys = self._index.keys()
        if not offset:
            keys = keys[-limit:]
        else:
            keys = keys[-(limit + offset):-offset]
        return map(self.getMessage, [str(self._index.get(x)) for x in keys])
        
    security.declareProtected(ViewBoard, 'getNumberOfMessages')
    def getNumberOfMessages(self):
        """
        Returns the number of messages to this conversation.
        """
        return len(self._index)

    security.declareProtected(ViewBoard, 'getLastMessageDate')
    def getLastMessageDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last message 
        for the conversation.
        """
        if len(self._index) > 0:
            return self.getMessage(str(self._index.get(self._index.maxKey()))).creation_date
        else:
            return None

    security.declareProtected(ViewBoard, 'getLastMessageAuthor')
    def getLastMessageAuthor(self):
        """
        Returns the name of the author of the last message.
        """
        if len(self._index) > 0:
            return self.getMessage(str(self._index.get(self._index.maxKey()))).Creator()
        else:
            return None

    security.declareProtected(ManageConversation, 'moveToForum')
    def moveToForum(self, forum_id):
        """Moves conversation to another forum"""
        forum = self.getForum().getBoard().getForum(forum_id)
        if forum:
            parent = self.getForum()
            cut_objects = parent.manage_cutObjects((self.getId(),) )
            forum.manage_pasteObjects(cut_objects)
            
    security.declareProtected(ManageConversation, 'delete')
    def delete(self):
        """"""
        parent = self.getForum()
        parent._delObject(self.getId())

    security.declareProtected(ViewBoard, 'Creator')
    def Creator(self):
        return getattr(self, '_creator', None) or SkinnedFolder.Creator(self)

    ############################################################################
    # Folder methods, indexes and such

    security.declareProtected(AddMessage, 'generateId')
    def generateId(self, prefix='item', suffix='', rand_ceiling=999999999, message=0, min_id=1):
        """Returns an ID not used yet by this folder.
        """
        if not message:
            return BTreeFolder2Base.generateId(self, prefix, suffix, rand_ceiling)
        else:
            tree = self._tree
            n = self._v_nextid
            if n is 0:
                if len(self._index) > 0:
                    n = self._index.get(self._index.maxKey()) + 1
                    if tree.has_key(str(n)):
                        n = len(self) + 1
                else:
                    n = 1
            try:
                min_id = int(min_id)
            except ValueError:
                min_id = 1
            n = max( n, min_id)
            attempt = 0
            while 1:
                if n % 4000 != 0 and n <= rand_ceiling:
                    id = '%d' % n
                    if not tree.has_key(id):
                        break
                n = randint(min_id, rand_ceiling)
                attempt = attempt + 1
                if attempt > MAX_UNIQUEID_ATTEMPTS:
                    # Prevent denial of service
                    raise ExhaustedUniqueIdsError
            self._v_nextid = n + 1
            return id

    security.declareProtected(ManageConversation, 'setDateKey')
    def setDateKey(self, id, date=DateTime()):
        """Update the _index."""
        result = self._index.setDateKey(id,date)
        # Update messagecount on forum aswell
        if result > 0:
            self.getForum().changeNumberOfMessages(result)
        return result
        
    security.declareProtected(ManageConversation, 'delDateKey')
    def delDateKey(self, id):
        """Delete key from indexes. """
        result = self._index.delDateKey(id)
        # Update messagecount on forum aswell
        if result > 0:
            self.getForum().changeNumberOfMessages(-result)
        return result

    def _checkId(self, id, allow_dup=0):
        SkinnedFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        BTreeFolder2Base._delOb(self, id, object)
        # Update Ploneboard specific indexes
        if IMessage.isImplementedBy(object):
            self.delDateKey(id)

    # Workflow related methods - called by workflow scripts to control what to display
    security.declareProtected(AddMessage, 'notifyPublished')
    def notifyPublished(self):
        """ Notify about publishing, so object can be added to index """
        self.aq_inner.aq_parent.setDateKey(self.id, self.getLastMessageDate() or DateTime())

    security.declareProtected(AddMessage, 'notifyRetracted')
    def notifyRetracted(self):
        """ Notify about retracting, so object can be removed from index """
        self.aq_inner.aq_parent.delDateKey(self.id)

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
        return (self.title, )
    
    def _getBoardCatalog(self):
        return self.getForum().getBoard().getInternalCatalog()

def addConversation(self
                  , id
                  , title=''):
    """Factory method for creating conversation."""
    fconversation = Conversation(id, title)
    self._setObject(id, fconversation)

Globals.InitializeClass(Conversation)

