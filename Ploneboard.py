"""
$Id: Ploneboard.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
"""

import Globals

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFCore.PortalContent import PortalContent
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Referenceable import Referenceable

import PloneboardCatalog
from PloneboardPermissions import ViewBoard, SearchBoard, \
     AddBoard, AddForum, ManageBoard, AddAttachment

from Forum import Forum

from interfaces import IPloneboard
from Products.Archetypes.interfaces.referenceable import IReferenceable

factory_type_information = \
( { 'id'             : 'Ploneboard'
  , 'meta_type'      : 'Ploneboard'
  , 'description'    : """Boards hold discussions."""
  , 'icon'           : 'ploneboard_icon.gif'
  , 'product'        : 'Ploneboard'
  , 'factory'        : 'addPloneboard'
  , 'filter_content_types' : 1
  , 'allowed_content_types' : ('Ploneboard Forum', ) 
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
    , { 'id'            : 'home'
      , 'name'          : 'Board Home'
      , 'action'        : 'string:${object_url}/board_view'
      , 'permissions'   : (ViewBoard,)
      , 'category'      : 'object'
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
      , 'category'      : 'object'
      }
    )
  },
)

# PortalFolder/SkinnedFolder overrides the catalogaware methods to avoid being 
# added to the catalog
class Ploneboard(Referenceable, CMFCatalogAware, SkinnedFolder, PortalContent):
    """
    Ploneboard is the outmost board object, what shows up in your site.
    """
    __implements__ = (IPloneboard, IReferenceable)

    meta_type = portal_type = 'Ploneboard'
    manage_options = SkinnedFolder.manage_options

    # CONFIG variables
    _number_of_attachments = 5

    security = ClassSecurityInfo()
    
    def __init__(self, id, title=''):
        self.id = id
        self.title = title
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
        forum = Forum(id, title)
        self._setObject(id, forum)
        
        forum = getattr(self, id)
        forum._setPortalTypeName('Ploneboard Forum')
        forum.notifyWorkflowCreated()
        forum.setDescription(description)

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

    def manage_afterAdd(self, item, container):
        Referenceable.manage_afterAdd(self, item, container)
        PortalContent.manage_afterAdd(self, item, container)

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item):
        Referenceable.manage_afterClone(self, item)
        PortalContent.manage_afterClone(self, item)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        Referenceable.manage_beforeDelete(self, item, container)
        PortalContent.manage_beforeDelete(self, item, container)


    ############################################################################
    # CONFIG
    
    security.declareProtected(AddAttachment, 'getNumberOfAttachments')
    def getNumberOfAttachments(self):
        """ 
        Returns number of allowed attachments
        """
        return self._number_of_attachments

def addPloneboard( self
                 , id
                 , title='' ):
    """Factory method for adding Ploneboard."""
    board = Ploneboard(id, title)
    self._setObject(id, board)

Globals.InitializeClass(Ploneboard)
