"""
$Id$
"""

# zope3, zope 2.8, or Five dependency
from zope.interface import implements

import Globals
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from Products.Ploneboard.config import PROJECTNAME

from Products.Ploneboard import PloneboardCatalog
from Products.Ploneboard.permissions import ViewBoard, SearchBoard, \
    AddBoard, AddForum, ManageBoard, AddAttachment  
from PloneboardForum import PloneboardForum
from Products.Ploneboard.interfaces import IPloneboard


schema = BaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              default_content_type = 'text/html',
              default_output_type = 'text/plain',
              widget = TextAreaWidget(description = "Enter a brief description of the board.",
                                      description_msgid = "help_description",
                                      i18n_domain = "ploneboard",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      rows = 5)),
    ))

class Ploneboard(BaseBTreeFolder):
    """
    Ploneboard is the outmost board object, what shows up in your site.
    """
    implements(IPloneboard) # XXX IBaseBTreeFolder

    meta_type = 'Ploneboard'
    archetype_name = 'Message Board'

    schema = schema

    content_icon = 'ploneboard_icon.gif'
    allowed_content_types = ('PloneboardForum',)

    _at_rename_after_creation = True

    actions = (
            { 'id'          : 'view'
            , 'name'        : 'View'
            , 'action'      : 'string:$object_url'
            , 'permissions' : (ViewBoard,)
            },
            { 'id'          : 'moderate'
            , 'name'        : 'Moderate'
            , 'action'      : 'string:$object_url/moderation_form'
            , 'permissions' : (ManageBoard,)
            }
        )

    aliases = \
        {
              '(Default)' : 'board_view'
            , 'view'      : 'board_view'
        }

    # CONFIG variables
    _number_of_attachments = 5

    security = ClassSecurityInfo()
    
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self._setupInternalCatalog()

    security.declareProtected(ManageBoard, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(ViewBoard, 'getBoard')
    def getBoard(self):
        """Returns self."""
        return self

    security.declareProtected(ViewBoard, 'getBoardTitle')
    def getBoardTitle(self):
        """Gets the title, useful to avoid manual acquisition from comments."""
        return self.Title()

    security.declareProtected(ViewBoard, 'getBoardDescription')
    def getBoardDescription(self):
        """Gets the description, useful to avoid manual acquisition from comments."""
        return self.Description()

    def _setupInternalCatalog(self):
        catalog = PloneboardCatalog.PloneboardCatalog()
        self._setObject(catalog.id, catalog)

    security.declareProtected(ViewBoard, 'getInternalCatalog')
    def getInternalCatalog(self):
        """ """
        return self._getOb(PloneboardCatalog.PLONEBOARD_CATALOG_ID)

    security.declareProtected(AddForum, 'addForum')
    def addForum( self
                , id
                , title
                , description ):
        """Add a forum to the board."""
        kwargs = {'title' : title, 'description' : description}
        forum = PloneboardForum(id)
        self._setObject(id, forum)
        forum = getattr(self, id)
        forum.initializeArchetype(**kwargs)
        forum._setPortalTypeName('PloneboardForum')
        forum.notifyWorkflowCreated()
        #forum.setDescription(description)
        return forum

    security.declarePublic('getForums')
    def getForums(self):
        """Return all the forums in this board."""
        return self.contentValues()

    security.declareProtected(ManageBoard, 'removeForum')
    def removeForum(self, forum_id):
        """Remove a forum from this board."""
        self._delObject(forum_id)

    security.declareProtected(SearchBoard, 'searchComments')
    def searchComments(self, query):
        """This method searches through all forums, conversations and comments."""
        # maybe we need return objects and not brains?
        return self.getInternalCatalog().searchResults(query)
    
    security.declarePublic('getForum')
    def getForum(self, forum_id):
        """Returns forum with specified forum id."""
        return getattr(self, forum_id, None)

    #def manage_afterAdd(self, item, container):
    #    BaseBTreeFolder.manage_afterAdd(self, item, container)

    #security.declarePrivate('manage_afterClone')
    #def manage_afterClone(self, item):
    #    BaseBTreeFolder.manage_afterClone(self, item, container)

    #security.declarePrivate('manage_beforeDelete')
    #def manage_beforeDelete(self, item, container):
    #    if aq_base(container) is not aq_base(self):
    #        self.__recurse('manage_beforeDelete', item, container)
    #    BaseBTreeFolder.manage_beforeDelete(self, item, container)

    #def __recurse(self, name, *args):
    #    """ Recurse in subobjects. """
    #    values = self.objectValues()
    #    for ob in values:
    #        s = getattr(ob, '_p_changed', 0)
    #        if hasattr(aq_base(ob), name):
    #            getattr(ob, name)(*args)
    #        if s is None: ob._p_deactivate()

    ############################################################################
    # CONFIG
    
    security.declareProtected(AddAttachment, 'getNumberOfAttachments')
    def getNumberOfAttachments(self):
        """ 
        Returns number of allowed attachments
        """
        return self._number_of_attachments

    def __nonzero__(self):
        return 1

registerType(Ploneboard, PROJECTNAME)
Globals.InitializeClass(Ploneboard)
