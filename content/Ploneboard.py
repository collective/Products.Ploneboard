"""
$Id$
"""

# zope3, zope 2.8, or Five dependency
from zope.interface import implements, providedBy

import Globals
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

from Products.Five.bridge import fromZ2Interface

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField, LinesField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget, LinesWidget

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFDynamicViewFTI.interfaces \
    import ISelectableBrowserDefault as ZopeTwoISelectableBrowserDefault
try:
    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
except ImportError:
    ISelectableBrowserDefault = fromZ2Interface(ZopeTwoISelectableBrowserDefault)

from Products.Ploneboard.config import PROJECTNAME
from Products.Ploneboard.permissions import ViewBoard, SearchBoard, \
    AddBoard, AddForum, ManageBoard, AddAttachment, ModerateForum
from Products.Ploneboard.content.PloneboardForum import PloneboardForum
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
    LinesField('categories',
               widget = LinesWidget(
                   description = "Enter the categories you want to have available for forums, one category on each line.",
                   description_msgid = "help_categories")
              ),
    ))

class Ploneboard(BrowserDefaultMixin, BaseBTreeFolder):
    """Ploneboard is the outmost board object, what shows up in your site."""
    implements(IPloneboard)
    __implements__ = (BrowserDefaultMixin.__implements__, BaseBTreeFolder.__implements__,)

    meta_type = 'Ploneboard'
    archetype_name = 'Message Board'

    schema = schema

    content_icon = 'ploneboard_icon.gif'
    allowed_content_types = ('PloneboardForum',)

    _at_rename_after_creation = True

    # Set up our views - these are available from the 'display' menu
    default_view = 'board_view'
    immediate_view = 'board_view'
    suppl_views = ('board_view', 'board_view_global')

    actions = (
            { 'id'          : 'view'
            , 'name'        : 'View'
            , 'action'      : 'string:$object_url'
            , 'permissions' : (ViewBoard,)
            },
            { 'id'          : 'edit'
            , 'name'        : 'Edit'
            , 'action'      : 'string:$object_url/edit'
            , 'permissions' : (ModifyPortalContent,)
            },
            { 'id'          : 'metadata'
            , 'name'        : 'Properties'
            , 'action'      : 'string:$object_url/properties'
            , 'permissions' : (ModifyPortalContent,)
            },
            { 'id'          : 'moderate'
            , 'name'        : 'Moderate'
            , 'action'      : 'string:$object_url/moderate'
            , 'permissions' : (ModerateForum,)
            },
        )

    aliases = \
        {
            '(Default)'  : '(dynamic view)',
            'view'       : '(selected layout)',
            'edit'       : 'base_edit',
            'properties' : 'base_metadata',
            'sharing'    : 'folder_localrole_form',
            'index.html' : '(dynamic view)',
            'moderate'   : 'moderation_form',
        }

    security = ClassSecurityInfo()
    
    def getCatalog(self):
        return getToolByName(self, 'portal_catalog')

    security.declareProtected(ManageBoard, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(AddForum, 'addForum')
    def addForum( self
                , id
                , title
                , description ):
        """Add a forum to the board.
        XXX get rid of this and use regular content creation
        as this also enables us to instantiate different types
        that implements the interface
        """
        kwargs = {'title' : title, 'description' : description}
        forum = PloneboardForum(id)
        self._setObject(id, forum)
        forum = getattr(self, id)
        forum.initializeArchetype(**kwargs)
        forum._setPortalTypeName('PloneboardForum')
        forum.notifyWorkflowCreated()
        # Enable topic syndication by default
        syn_tool = getToolByName(self, 'portal_syndication', None)
        if syn_tool is not None:
            if (syn_tool.isSiteSyndicationAllowed() and not syn_tool.isSyndicationAllowed(forum)):
                syn_tool.enableSyndication(forum)

        #forum.setDescription(description)
        return forum

    security.declareProtected(ViewBoard, 'getForums')
    def getForums(self, sitewide=False):
        """Return all the forums in this board."""
        query = {'object_implements':'Products.Ploneboard.interfaces.IForum'}
        if not sitewide:
            query['path'] = '/'.join(self.getPhysicalPath())
        return [f.getObject() for f in self.getCatalog()(query)]


    security.declareProtected(ViewBoard, 'getForumIds')
    def getForumIds(self):
        """Return all the forums in this board."""
        return [f.getId for f in self.getCatalog()(
                object_implements='Products.Ploneboard.interfaces.IForum')]

    security.declareProtected(ManageBoard, 'removeForum')
    def removeForum(self, forum_id):
        """Remove a forum from this board."""
        self._delObject(forum_id)

    security.declareProtected(SearchBoard, 'searchComments')
    def searchComments(self, query):
        """This method searches through all forums, conversations and comments."""
        return self.getCatalog()(**query)
    
    security.declarePublic('getForum')
    def getForum(self, forum_id):
        """Returns forum with specified forum id."""
        #return getattr(self, forum_id, None)
        forums = self.getCatalog()(
                object_implements='Products.Ploneboard.interfaces.IForum',
                getId=forum_id)
        if forums:
            return forums[0].getObject()
        else:
            return None

    def __nonzero__(self):
        return 1

registerType(Ploneboard, PROJECTNAME)
