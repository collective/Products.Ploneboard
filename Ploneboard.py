"""
$Id: Ploneboard.py,v 1.3 2004/03/15 01:58:41 limi Exp $
"""

import Globals
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from config import PROJECTNAME

import PloneboardCatalog
from PloneboardPermissions import ViewBoard, SearchBoard, \
    AddBoard, AddForum, ManageBoard, AddAttachment  
from PloneboardForum import PloneboardForum
from interfaces import IPloneboard


factory_type_information = \
( { 'id'             : 'Ploneboard'
  , 'meta_type'      : 'Ploneboard'
  , 'description'    : """Boards hold discussions."""
  , 'icon'           : 'ploneboard_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'factory'        : 'addPloneboard'
  , 'filter_content_types' : 1
  , 'allowed_content_types' : ('PloneboardForum', ) 
  , 'immediate_view' : 'board_edit_form'
  , 'aliases'        : {'(Default)':'board_view',
                        'view':'board_view'}
  , 'actions'        :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'string:${object_url}/board_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'string:${object_url}/board_edit_form'
      , 'permissions'   : (ManageBoard,)
      , 'category'      : 'folder'
      }
    , { 'id'            : 'add_forum'
      , 'name'          : 'Add Forum'
      , 'action'        : 'string:${object_url}/add_forum_form'
      , 'permissions'   : (AddForum,)
      , 'category'      : 'object_actions'
      }
    )
  },
)

schema = BaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              default_content_type = 'text/plain',
              default_output_type = 'text/html',
              widget = TextAreaWidget(description = "Enter a brief description of the board.",
                                      description_msgid = "help_description",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      rows = 5)),
    ))

class Ploneboard(BaseBTreeFolder):
    """
    Ploneboard is the outmost board object, what shows up in your site.
    """
    __implements__ = (IPloneboard,) + tuple(BaseBTreeFolder.__implements__)
    
    archetype_name = 'Ploneboard'

    schema = schema
    
    # CONFIG variables
    _number_of_attachments = 5

    security = ClassSecurityInfo()
    
    def __init__(self, oid, **kwargs):
        BaseBTreeFolder.__init__(self, oid, **kwargs)
        self._setupInternalCatalog()

    def _setupInternalCatalog(self):
        catalog = PloneboardCatalog.PloneboardCatalog()
        self._setObject(catalog.id, catalog)

    security.declareProtected(ViewBoard, 'getInternalCatalog')
    def getInternalCatalog(self):
        """ """
        return self._getOb(PloneboardCatalog.PLONEBOARD_CATALOG_ID)

    security.declareProtected(AddBoard, 'addForum')    
    def addForum( self
                , id
                , title
                , description ):
        """Add a forum to the board."""
        kwargs = {'title' : title, 'description' : description}
        forum = PloneboardForum(id, **kwargs)
        self._setObject(id, forum)
        
        forum = getattr(self, id)
        forum._setPortalTypeName('PloneboardForum')
        forum.notifyWorkflowCreated()
        #forum.setDescription(description)
        return forum

    security.declarePublic('getForums')
    def getForums(self):
        return self.contentValues()

    security.declareProtected(ManageBoard, 'removeForum')
    def removeForum(self, forum_id):
        """Remove a forum from this board."""
        self._delObject(forum_id)

    security.declareProtected(SearchBoard, 'searchMessages')
    def searchMessages(self, query):
        """This method searches through all forums, conversations and messages."""
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

registerType(Ploneboard, PROJECTNAME)
Globals.InitializeClass(Ploneboard)
