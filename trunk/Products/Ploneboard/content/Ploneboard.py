from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import LinesWidget
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Ploneboard import utils
from Products.Ploneboard.config import PROJECTNAME
from Products.Ploneboard.content.PloneboardForum import PloneboardForum
from Products.Ploneboard.interfaces import IPloneboard
from Products.Ploneboard.permissions import AddForum
from Products.Ploneboard.permissions import ManageBoard
from Products.Ploneboard.permissions import SearchBoard
from Products.Ploneboard.permissions import ViewBoard

schema = ATBTreeFolderSchema + Schema((
    TextField('description',
        searchable = 1,
        default_content_type = 'text/html',
        default_output_type = 'text/plain',
        widget = TextAreaWidget(
                description = "Enter a brief description of the board.",
                description_msgid = "help_description_board",
                i18n_domain = "ploneboard",
                label = "Description",
                label_msgid = "label_description_board",
                rows = 5
                )
            ),

    LinesField('categories',
        widget = LinesWidget(
            description = \
                "Enter the categories you want to have available for "
                "forums, one category on each line.",
            description_msgid = "help_categories_board",
            label = "Categories",
            label_msgid = "label_categories_board",
            i18n_domain = "ploneboard")),
    ))

utils.finalizeSchema(schema)


class Ploneboard(BrowserDefaultMixin, ATBTreeFolder):
    """Ploneboard is the outmost board object, what shows up in your site."""
    implements(IPloneboard)
    meta_type = 'Ploneboard'
    schema = schema
    _at_rename_after_creation = True

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

        XXX: Should be possible to parameterise the exact type that is being
        added.
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
        query = {'object_provides':'Products.Ploneboard.interfaces.IForum'}
        if not sitewide:
            query['path'] = '/'.join(self.getPhysicalPath())
        return [f.getObject() for f in self.getCatalog()(query)]


    security.declareProtected(ViewBoard, 'getForumIds')
    def getForumIds(self):
        """Return all the forums in this board."""
        return [f.getId for f in self.getCatalog()(
                object_provides='Products.Ploneboard.interfaces.IForum')]

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
                object_provides='Products.Ploneboard.interfaces.IForum',
                getId=forum_id)
        if forums:
            return forums[0].getObject()
        else:
            return None

    def __nonzero__(self):
        return 1

registerType(Ploneboard, PROJECTNAME)
