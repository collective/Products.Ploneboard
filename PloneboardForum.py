"""
$Id: PloneboardForum.py,v 1.4 2004/03/24 15:50:15 tesdal Exp $
"""

from random import randint

import sys
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DateTime import DateTime

from BTrees.Length import Length

from Products.ZCatalog.Lazy import LazyMap

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from config import PROJECTNAME

from PloneboardPermissions import ViewBoard, SearchBoard, \
     AddForum, ManageForum, ManageBoard, AddMessage
from PloneboardConversation import PloneboardConversation
from PloneboardIndex import PloneboardIndex
from interfaces import IForum, IConversation

factory_type_information = \
( { 'id'             : 'PloneboardForum'
  , 'meta_type'      : 'PloneboardForum'
  , 'description'    : """Forums hold conversations."""
  , 'icon'           : 'ploneboard_forum_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'global_allow'   : 0 # To avoid it being visible in add contents menu
  , 'filter_content_types' : 1
  , 'allowed_content_types' : ('PloneboardConversation', ) 
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

schema = BaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              default_content_type = 'text/plain',
              default_output_type = 'text/html',
              widget = TextAreaWidget(description = "Enter a brief description of the forum.",
                                      description_msgid = "help_description",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      rows = 5)),
    ))

class ForumIndex(PloneboardIndex):
    """
    A class for containing the date indexes and handling length (map to __len__)
    """
    def _calculateInternalDateKey(self, date):
        # Date key - use max int minus seconds since epoch as key in date index
        return sys.maxint - int(date)


MAX_UNIQUEID_ATTEMPTS = 1000

class PloneboardForum(BaseBTreeFolder):
    """
    A Forum contains conversations.
    """
    
    __implements__ = (IForum,) + tuple(BaseBTreeFolder.__implements__)

    archetype_name = 'Ploneboard Forum'
    
    schema = schema
    
    _index = None
    _message_count = None

    _moderated = 0 # 1 if moderated

    security = ClassSecurityInfo()
    
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        # Archetypes doesn't set values on creation from kwargs
        self.setTitle(kwargs.get('title', ''))
        self.setDescription(kwargs.get('description', ''))
        self._index = ForumIndex()
        self._message_count = Length()
        self._moderated = 0

    security.declareProtected(ViewBoard, 'getForum')
    def getForum(self):
        """Returns self."""
        return self

    security.declareProtected(ViewBoard, 'getForumTitle')
    def getForumTitle(self):
        """Gets the title, useful to avoid manual acquisition from messages."""
        return self.Title()

    security.declareProtected(ViewBoard, 'getForumDescription')
    def getForumDescription(self):
        """Gets the description, useful to avoid manual acquisition from messages."""
        return self.Description()

    security.declareProtected(AddMessage, 'addConversation')
    def addConversation(self, subject, messagesubject=None, body=None, creator=None, script=1):
        """Adds a new conversation to the forum."""
        # Add a new conversation and a message inside it.
        # Only create message if body is not None
        id = self.generateId(conversation=1)
        kwargs = {'title' : subject, 'creator' : creator}
        conversation = PloneboardConversation(id, **kwargs)
        self._setObject(id, conversation)
        conversation = getattr(self, id)
        conversation._setPortalTypeName('PloneboardConversation')
        conversation.notifyWorkflowCreated()
        if body:
            if not messagesubject:
                messagesubject = subject
            if script:
                conversation.add_message_script(messagesubject, body, creator)
            else:
                conversation.addMessage(messagesubject, body, creator)
        return conversation

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
            return BaseBTreeFolder.generateId(self, prefix, suffix, rand_ceiling)
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
        BaseBTreeFolder._checkId(self, id, allow_dup)

    def setDateKey(self, id, date=None):
        """Update the _index."""
        self._index.setDateKey(id,date)


    def delDateKey(self, id):
        """Delete key from _index. """
        self._index.delDateKey(id)
        
    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        object = self.getConversation(id)
        BaseBTreeFolder._delOb(self, id)
        # Update Ploneboard specific indexes
        if IConversation.isImplementedBy(object):
            self.delDateKey(id)


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
        BaseBTreeFolder.manage_beforeDelete(self, item, container)    

    def SearchableText(self):
        """ """
        return (self.Title(), )
    
    def _getBoardCatalog(self):
        return self.getBoard().getInternalCatalog()

registerType(PloneboardForum, PROJECTNAME)
Globals.InitializeClass(PloneboardForum)

