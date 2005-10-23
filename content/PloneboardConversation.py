"""
$Id$
"""

# zope3, zope 2.8, or Five dependency
from zope.interface import implements

from random import randint
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DateTime import DateTime

from Products.ZCatalog.Lazy import LazyMap

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from Products.Ploneboard.config import PROJECTNAME

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Ploneboard.permissions import ViewBoard, SearchBoard, ManageForum,\
     ManageBoard, AddConversation, AddComment, ManageConversation
from PloneboardComment import PloneboardComment
from PloneboardIndex import PloneboardIndex
from Products.Ploneboard.interfaces import IConversation, IComment
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder

PBConversationBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBConversationBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBConversationBaseBTreeFolderSchema['title'].write_permission = AddConversation


schema = PBConversationBaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              read_permission = ViewBoard,
              write_permission = AddConversation,
              default_content_type = 'text/plain',
              default_output_type = 'text/html',
              widget = TextAreaWidget(description = "Enter a brief description of the conversation.",
                                      description_msgid = "help_description",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      rows = 5)),
    ))

    
class ConversationIndex(PloneboardIndex):
    """
    A class for containing the date indexes and handling length (map to __len__)
    """
    def _calculateInternalDateKey(self, date):
        # Date key as int
        return int(date)


MAX_UNIQUEID_ATTEMPTS = 1000

class PloneboardConversation(BrowserDefaultMixin, BaseBTreeFolder):
    """
    Conversation contains comments.
    """

    implements(IConversation) # XXX IBaseBTreeFolder
    __implements__ = (INonStructuralFolder,) + BaseBTreeFolder.__implements__

    meta_type = 'PloneboardConversation'
    archetype_name = 'Conversation'

    schema = schema

    content_icon = 'ploneboard_conversation_icon.gif'
    allowed_content_types = ('PloneboardComment',)
    global_allow = 0 # To avoid it being visible in the add contents menu

    # Set up our views - these are available from the 'display' menu
    default_view = 'threaded_conversation_view'
    immediate_view = 'threaded_conversation_view'
    suppl_views = ('conversation_view', 'threaded_conversation_view')

    actions = (
            { 'id'          : 'view'
            , 'name'        : 'View'
            , 'action'      : 'string:$object_url'
            , 'permissions' : (ViewBoard,)
            },
        )

    aliases = {
            '(Default)'  : '(dynamic view)',
            'view'       : '(selected layout)',
            'index.html' : '(dynamic view)',
            'edit'       : 'base_edit',
            'properties' : 'base_metadata',
            'sharing'    : 'folder_localrole_form',
            'gethtml'    : '',
            'mkdir'      : '',
        }

    _index = None

    security = ClassSecurityInfo()
    
    #def __init__(self, id, title='', creator=None):
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self._index = ConversationIndex()

    security.declareProtected(ManageConversation, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(ViewBoard, 'getConversation')
    def getConversation(self):
        """Returns self."""
        return self
    
    security.declareProtected(ViewBoard, 'getConversationTitle')
    def getConversationTitle(self):
        """Gets the title, useful to avoid manual acquisition from comments."""
        return self.Title()

    security.declareProtected(AddComment, 'addComment')
    def addComment( self, comment_subject, comment_body, creator=None ):
        """Adds a new comment with subject and body."""
        id = self.generateId(comment=1)
        if not comment_subject:
            comment_subject = self.Title()
        kwargs = {'title' : comment_subject, 
                  'creator' : creator,
                  'text' : comment_body
                  }
        #comment = PloneboardComment(id, comment_subject, comment_body, creator)
        comment = PloneboardComment(id)
        self._setObject(id, comment)
        m = getattr(self, id)
        m.initializeArchetype(**kwargs)
        m._setPortalTypeName('PloneboardComment')
        m.notifyWorkflowCreated()
        return m
    
    security.declareProtected(ViewBoard, 'getComment')
    def getComment(self, comment_id, default=None):
        """Returns the comment with the specified id."""
        return self._getOb(comment_id, default)
    
    security.declareProtected(ViewBoard, 'getComments')
    def getComments(self, limit=30, offset=0, **kw):
        """
        Retrieves the specified number of comments with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        keys = self._index.keys()
        if not offset:
            keys = keys[-limit:]
        else:
            keys = keys[-(limit + offset):-offset]
        return map(self.getComment, [str(self._index.get(x)) for x in keys])
        
    security.declareProtected(ViewBoard, 'getNumberOfComments')
    def getNumberOfComments(self):
        """
        Returns the number of comments in this conversation.
        """
        return len(self._index)

    security.declareProtected(ViewBoard, 'getNumberOfReplies')
    def getNumberOfReplies(self):
        """
        Returns the number of replies for this conversation.
        """
        return len(self._index)-1

    security.declareProtected(ViewBoard, 'getLastCommentDate')
    def getLastCommentDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last comment 
        for the conversation.
        """
        if len(self._index) > 0:
            return self.getComment(str(self._index.get(self._index.maxKey()))).creation_date
        else:
            return None

    security.declareProtected(ViewBoard, 'getLastCommentAuthor')
    def getLastCommentAuthor(self):
        """
        Returns the name of the author of the last comment.
        """
        if len(self._index) > 0:
            return self.getComment(str(self._index.get(self._index.maxKey()))).Creator()
        else:
            return None

    security.declareProtected(ViewBoard, 'getThreadedComments')
    def getThreadedComments(self):
        """
        See IConversation.getThreadedComments.__doc__
        """
        # Shamelessly taken from portal_skins/plone_scripts/getReplyReplies
        def getRs(comment, replies, counter):
            rs = comment.getReplies()
            #rs = container.sort_modified_ascending(rs)
            for r in rs:
                comment_id = r.getId()
                if self._isIdIndexed(comment_id):
                    replies.append({'depth':counter, 'object':r})
                    getRs(r, replies, counter=counter + 1)
        comment1 = self.getFirstComment()
        replies = [{'depth':0, 'object':comment1},]
        getRs(comment1, replies, 1)
        return replies

    security.declareProtected(ViewBoard, 'getFirstComment')
    def getFirstComment(self):
        """
        See IConversation.getFirstComment.__doc__
        """
        if len(self._index) > 0:
            return self.getComment( str( self._index.get( self._index.minKey() ) ) )
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
        return getattr(self, '_creator', None) or BaseBTreeFolder.Creator(self)

    def _isIdIndexed(self, id):
        """Check to see if the comment id is in the reverse index.
        """
        id = int(id)
        return self._index._reverse_dates.has_key(id)

    ############################################################################
    # Folder methods, indexes and such

    security.declareProtected(AddComment, 'generateId')
    def generateId(self, prefix='item', suffix='', rand_ceiling=999999999, comment=0, min_id=1):
        """Returns an ID not used yet by this folder.
        """
        if not comment:
            return BaseBTreeFolder.generateId(self, prefix, suffix, rand_ceiling)
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
        # Update commentcount on forum aswell
        if result > 0:
            self.getForum().changeNumberOfComments(result)
        return result
        
    security.declareProtected(ManageConversation, 'delDateKey')
    def delDateKey(self, id):
        """Delete key from indexes. """
        result = self._index.delDateKey(id)
        # Update commentcount on forum aswell
        if result > 0:
            self.getForum().changeNumberOfComments(-result)
        return result

    def _checkId(self, id, allow_dup=0):
        BaseBTreeFolder._checkId(self, id, allow_dup)

    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        object = self.getComment(id)
        BaseBTreeFolder._delOb(self, id)
        # Update Ploneboard specific indexes
        if IComment.isImplementedBy(object):
            self.delDateKey(id)
            
    def _delObject(self, id, dp=1, recursive=0):
        """Deletes object and if recursive is true - its descendants"""
        # We need to delete all descendants of comment if recursive is true
        if recursive:
            object = self.getComment(id)
            for msg_id in object.childIds():
                BaseBTreeFolder._delObject(self, msg_id)
        BaseBTreeFolder._delObject(self, id)
        # we delete ourselves if we don't have any comments
        if self.getNumberOfComments() == 0:
            self.getForum()._delObject(self.getId())

    # Workflow related methods - called by workflow scripts to control what to display
    security.declareProtected(AddComment, 'notifyPublished')
    def notifyPublished(self):
        """ Notify about publishing, so object can be added to index """
        # This notifies the containing forum
        self.getForum().setDateKey(self.id, self.getLastCommentDate() or DateTime())

    security.declareProtected(AddComment, 'notifyRetracted')
    def notifyRetracted(self):
        """ Notify about retracting, so object can be removed from index """
        # This notifies the containing forum
        self.getForum().delDateKey(self.id)

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
        return (self.Title(), )
    
    def _getBoardCatalog(self):
        return self.getForum().getBoard().getInternalCatalog()

    def __nonzero__(self):
        return 1

registerType(PloneboardConversation, PROJECTNAME)
Globals.InitializeClass(PloneboardConversation)
