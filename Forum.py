"""
$Id: Forum.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
"""

from random import randint

import Globals, sys

from Acquisition import aq_base
from DateTime import DateTime

from BTrees.Length import Length

from Products.ZCatalog.Lazy import LazyMap

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFCore.PortalContent import PortalContent
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Referenceable import Referenceable

from PloneboardPermissions import ViewBoard, SearchBoard, \
     AddForum, ManageForum, ManageBoard, AddMessage
from Conversation import Conversation
from PloneboardIndex import PloneboardIndex
from interfaces import IForum, IConversation
from Products.Archetypes.interfaces.referenceable import IReferenceable

factory_type_information = \
( { 'id'             : 'Ploneboard Forum'
  , 'meta_type'      : 'Ploneboard Forum'
  , 'description'    : """Forums hold conversations."""
  , 'icon'           : 'ploneboard_forum_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'factory'        : None # To avoid it being visible in add contents menu
  , 'filter_content_types' : 1
  , 'allowed_content_types' : ('Ploneboard Conversation', ) 
  , 'immediate_view' : 'forum_edit_form'
  , 'aliases'        : {'(Default)':'forum_view',
                        'view':'forum_view'}
  , 'actions'        :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'string:${object_url}/forum_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'string:${object_url}/forum_edit_form'
      , 'permissions'   : (ManageBoard,)
      , 'category'      : 'folder'
      }
    )
  },
)

class ForumIndex(PloneboardIndex):
    """
    A class for containing the date indexes and handling length (map to __len__)
    """
    def _calculateInternalDateKey(self, date):
        # Date key - use max int minus seconds since epoch as key in date index
        return sys.maxint - int(date)


MAX_UNIQUEID_ATTEMPTS = 1000

class Forum(Referenceable, BTreeFolder2Base, SkinnedFolder, PortalContent):
    """
    A Forum contains conversations.
    """
    
    __implements__ = (IForum, IReferenceable)

    meta_type = 'Ploneboard Forum'
    manage_options = SkinnedFolder.manage_options

    security = ClassSecurityInfo()

    _index = None
    _message_count = None

    _moderated = 0 # 1 if moderated

    def __init__(self, id, title=''):
        SkinnedFolder.__init__(self, id, title)
        BTreeFolder2Base.__init__(self, id)
        self._index = ForumIndex()
        self._message_count = Length()
        self._moderated = 0

    security.declareProtected(ViewBoard, 'getBoard')
    def getBoard(self):
        """Gets the containing board."""
        return self.aq_inner.aq_parent

    security.declareProtected(AddMessage, 'addConversation')
    def addConversation(self, subject, body, creator=None, **kw):
        """Adds a new conversation to the forum."""
        # Add a new conversation and a message inside it.
        id = self.generateId(conversation=1)
        fconversation = Conversation(id, subject, creator)
        self._setObject(id, fconversation)
        m = getattr(self, id)
        m._setPortalTypeName('Ploneboard Conversation')
        m.notifyWorkflowCreated()
        #m.addMessage(subject, body)
        m.add_message_script(subject, body, creator)
        return m

    security.declareProtected(ViewBoard, 'getConversation')
    def getConversation(self, conversation_id, default=None):
        """Returns the conversation with the given conversation id."""
        return self._getOb(conversation_id, default)
    
    security.declareProtected(ManageForum, 'removeConversation')
    def removeConversation(self, conversation_id):
        """Removes a conversation with the given conversation id from the forum."""
        self._delObject(conversation_id)
    
    security.declareProtected(ViewBoard, 'getConversations')
    def getConversations(self, limit=20, offset=0):
        """Returns conversations."""
        keys = self._index.keys()
        keys = keys[offset:limit]
        return map(self.getConversation, [str(self._index.get(x)) for x in keys])

    security.declareProtected(ViewBoard, 'getNumberOfConversations')
    def getNumberOfConversations(self):
        """Returns the number of conversations in this forum."""
        return len(self._index)

    security.declareProtected(ViewBoard, 'changeNumberOfMessages')
    def changeNumberOfMessages(self, change):
        self._message_count.change(change)
    
    security.declareProtected(ViewBoard, 'getNumberOfMessages')
    def getNumberOfMessages(self):
        """Returns the number of messages to this forum."""
        return self._message_count()

    security.declareProtected(ViewBoard, 'getLastConversation')
    def getLastConversation(self):
        """
        Returns the last conversation.
        """
        if len(self._index) > 0:
            return self.getConversation(str(self._index.get(self._index.minKey())))
        else:
            return None

    security.declareProtected(ViewBoard, 'getLastMessageDate')
    def getLastMessageDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last message 
        for the forum.
        """
        return len(self._index) and self.getLastConversation().getLastMessageDate() or None

    security.declareProtected(ViewBoard, 'getLastMessageAuthor')
    def getLastMessageAuthor(self):
        """
        Returns the name of the author of the last message.
        """
        return self.getLastConversation() and self.getLastConversation().getLastMessageAuthor() or None


    def isModerated(self):
        """
        Returns true if the board is moderated
        """
        return self._moderated

    def setModerated(self, moderated):
        self._moderated = moderated

    ############################################################################
    # Folder methods, indexes and such

    security.declareProtected(AddMessage, 'generateId')
    def generateId(self, prefix='item', suffix='', rand_ceiling=999999999, conversation=0, min_id=1):
        """Returns an ID not used yet by this folder.
        """
        if not conversation:
            return BTreeFolder2Base.generateId(self, prefix, suffix, rand_ceiling)
        else:
            tree = self._tree
            n = self._v_nextid
            if n is 0:
                if len(self._index) > 0:
                    n = len(self._index)
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

    def _checkId(self, id, allow_dup=0):
        SkinnedFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

    def setDateKey(self, id, date=None):
        """Update the _index."""
        self._index.setDateKey(id,date)


    def delDateKey(self, id):
        """Delete key from _index. """
        self._index.delDateKey(id)
        
    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        BTreeFolder2Base._delOb(self, id, object)
        # Update Ploneboard specific indexes
        if IConversation.isImplementedBy(object):
            self.delDateKey(id)


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
        return self.getBoard().getInternalCatalog()

def addForum(self
             , id
             , title=''):
    """Factory method for creating forum."""
    forum = Forum(id, title)
    self._setObject(id, forum)

Globals.InitializeClass(Forum)
