"""
$Id$
"""

# zope3, zope 2.8, or Five dependency
from zope.interface import implements

from Products.Five.bridge import fromZ2Interface

from random import randint
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_chain
from DateTime import DateTime
from OFS.Image import File

from Products.ZCatalog.Lazy import LazyMap

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from Products.Ploneboard.config import PROJECTNAME, PLONEBOARD_CATALOG

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Ploneboard.permissions import ViewBoard, SearchBoard, ManageForum,\
     ManageBoard, AddConversation, AddComment, ManageConversation
from PloneboardComment import PloneboardComment
from PloneboardIndex import PloneboardIndex
from Products.Ploneboard.interfaces import IForum, IConversation, IComment

from Products.CMFPlone.interfaces.NonStructuralFolder \
    import INonStructuralFolder as ZopeTwoINonStructuralFolder
try:
    from Products.CMFPlone.interfaces.structure import INonStructuralFolder
except ImportError:
    INonStructuralFolder = fromZ2Interface(ZopeTwoINonStructuralFolder)

PBConversationBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBConversationBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBConversationBaseBTreeFolderSchema['title'].write_permission = AddConversation

from Products.CMFPlone.interfaces.NonStructuralFolder \
    import INonStructuralFolder as ZopeTwoINonStructuralFolder
try:
    from Products.CMFPlone.interfaces.structure import INonStructuralFolder
except ImportError:
    INonStructuralFolder = fromZ2Interface(ZopeTwoINonStructuralFolder)

schema = PBConversationBaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              read_permission = ViewBoard,
              write_permission = AddConversation,
              default_content_type = 'text/plain',
              default_output_type = 'text/plain',
              widget = TextAreaWidget(description = "Enter a brief description of the conversation.",
                                      description_msgid = "help_description_conversation",
                                      label = "Description",
                                      label_msgid = "label_description_conversation",
                                      i18n_domain = "ploneboard",
                                      rows = 5)),
    ))

    
MAX_UNIQUEID_ATTEMPTS = 1000


class PloneboardConversation(BrowserDefaultMixin, BaseBTreeFolder):
    """Conversation contains comments."""

    implements(IConversation, INonStructuralFolder)
    __implements__ = (BaseBTreeFolder.__implements__, BrowserDefaultMixin.__implements__, ZopeTwoINonStructuralFolder)

    meta_type = 'PloneboardConversation'
    archetype_name = 'Conversation'

    schema = schema

    content_icon = 'ploneboard_conversation_icon.gif'
    allowed_content_types = ('PloneboardComment',)
    global_allow = 0 # To avoid it being visible in the add contents menu

    # Set up our views - these are available from the 'display' menu
    default_view = 'conversation_view'
    immediate_view = 'conversation_view'
    suppl_views = ('conversation_view', 'threaded_conversation_view')

    _at_rename_after_creation = True

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

    security = ClassSecurityInfo()
    
    security.declareProtected(ManageConversation, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(ViewBoard, 'getTitle')
    def getTitle(self):
        """Get the title of this conversation"""
        return self.Title()

    security.declareProtected(ViewBoard, 'getForum')
    def getForum(self):
        """Returns containing forum."""
        # Try containment
        stoptypes = ['Plone Site']
        for obj in aq_chain(aq_inner(self)):
            if hasattr(obj, 'portal_type') and obj.portal_type not in stoptypes:
                if IForum.providedBy(obj):
                    return obj
        return None

    security.declareProtected(ManageConversation, 'removeComment')
    def removeComment( self, comment):
        self.manage_delObjects([comment.getId()])
        # TODO: reparent replies to this comment ?

    security.declareProtected(AddComment, 'addComment')
    def addComment( self, title, text, creator=None, files=None):
        """Adds a new comment with subject and body."""
        id = self.generateId()
        if not title:
            title = self.Title()
        kwargs = {'title' : title, 
                  'creators' : [creator],
                  'text' : text
                  }

        m = _createObjectByType('PloneboardComment', self, id, **kwargs)

        # Create files in message
        if files:
            for file in files:
                # Get raw filedata, not persistent object with reference to tempstorage
                attachment = File(file.getId(), file.title_or_id(), str(file.data), file.getContentType())
                m.addAttachment(attachment)

        return m
    
    security.declareProtected(ViewBoard, 'getComment')
    def getComment(self, comment_id, default=None):
        """Returns the comment with the specified id."""
        #return self._getOb(comment_id, default)
        comments = getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IComment', getId=comment_id)
        if comments:
            return comments[0].getObject()
        else:
            return None
    
    security.declareProtected(ViewBoard, 'getComments')
    def getComments(self, limit=30, offset=0, **kw):
        """
        Retrieves the specified number of comments with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        query = {'object_implements' : 'IComment',
                 'sort_on'           : 'created',
                 'sort_limit'        : (offset+limit),
                 'path'              : '/'.join(self.getPhysicalPath()),}
        query.update(kw)
        catalog=getToolByName(self, PLONEBOARD_CATALOG)
        return [f.getObject() for f in catalog(**query)[offset:offset+limit]]
        
    security.declareProtected(ViewBoard, 'getNumberOfComments')
    def getNumberOfComments(self):
        """
        Returns the number of comments in this conversation.
        """
        return len(getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IComment', path='/'.join(self.getPhysicalPath())))

    security.declareProtected(ViewBoard, 'getLastCommentDate')
    def getLastCommentDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last comment 
        for the conversation.
        """
        res = getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IComment', sort_on='created', sort_order='reverse', sort_limit=1, path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject().created()
        else:
            return None

    security.declareProtected(ViewBoard, 'getLastCommentAuthor')
    def getLastCommentAuthor(self):
        """
        Returns the name of the author of the last comment.
        XXX Interface method?
        """
        # XXX Tell the catalog the number of results we need to make sorting more efficient
        res = getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IComment', sort_on='created', sort_order='reverse', sort_limit=1, path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject().Creator()
        else:
            return None

    security.declareProtected(ViewBoard, 'getRootComments')
    def getRootComments(self):
        """
        Return a list all comments rooted to the board; ie comments which
        are not replies to other comments.
        """
        raw = self.getComments()
        ours = [ comment for comment in raw if comment.inReplyToUID() is None]
        return ours


    security.declareProtected(ViewBoard, 'getFirstComment')
    def getFirstComment(self):
        """
        See IConversation.getFirstComment.__doc__
        """
        res = getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IComment', sort_on='created', sort_limit=1, path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject()
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
        # XXX Should be handled by AT now.
        return getattr(self, '_creator', None) or BaseBTreeFolder.Creator(self)

    def __nonzero__(self):
        return 1
    
    # No setting of default page - makes no sense
    def canSetDefaultPage(self):
        return False

registerType(PloneboardConversation, PROJECTNAME)
