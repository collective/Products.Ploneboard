"""
$Id$
"""

# zope3, zope 2.8, or Five dependency
from zope.interface import implements, providedBy

import Globals
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from Products.Five.bridge import fromZ2Interface

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField, LinesField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget, LinesWidget

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault

from Products.Ploneboard.config import PROJECTNAME, PLONEBOARD_CATALOG
from Products.Ploneboard import PloneboardCatalog
from Products.Ploneboard.permissions import ViewBoard, SearchBoard, \
    AddBoard, AddForum, ManageBoard, AddAttachment  
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
                   descriptoin_msgid = "help_categories")
              ),
    ))

class Ploneboard(BrowserDefaultMixin, BaseBTreeFolder):
    """Ploneboard is the outmost board object, what shows up in your site."""
    implements((IPloneboard, fromZ2Interface(ISelectableBrowserDefault),))

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
        )

    aliases = \
        {
            '(Default)'  : '(dynamic view)',
            'view'       : '(selected layout)',
            'index.html' : '(dynamic view)',
        }

    security = ClassSecurityInfo()
    
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
        query = {'object_implements':'IForum'}
        if not sitewide:
            query['path'] = '/'.join(self.getPhysicalPath())
        return [f.getObject() for f in getToolByName(self, PLONEBOARD_CATALOG)(query)]


    security.declareProtected(ViewBoard, 'getForumIds')
    def getForumIds(self):
        """Return all the forums in this board."""
        return [f.getId for f in getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IForum')]

    security.declareProtected(ManageBoard, 'removeForum')
    def removeForum(self, forum_id):
        """Remove a forum from this board."""
        self._delObject(forum_id)

    security.declareProtected(SearchBoard, 'searchComments')
    def searchComments(self, query):
        """This method searches through all forums, conversations and comments."""
        # XXX Use the global board catalog for this
        return getToolByName(self, PLONEBOARD_CATALOG)(**query)
    
    security.declarePublic('getForum')
    def getForum(self, forum_id):
        """Returns forum with specified forum id."""
        #return getattr(self, forum_id, None)
        forums = getToolByName(self, PLONEBOARD_CATALOG)(object_implements='IForum', getId=forum_id)
        if forums:
            return forums[0].getObject()
        else:
            return None

    def __nonzero__(self):
        return 1

registerType(Ploneboard, PROJECTNAME)
