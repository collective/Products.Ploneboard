from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain
from Acquisition import aq_inner
from OFS.CopySupport import _cb_decode
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import CopyContainer
from OFS.CopySupport import CopyError
from OFS.Image import File
from OFS.Moniker import Moniker
from plone import api
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import BaseBTreeFolder
from Products.Archetypes.public import BaseBTreeFolderSchema
from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.CMFCore.permissions import View
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard import utils
from Products.Ploneboard.config import PROJECTNAME
from Products.Ploneboard.interfaces import IComment
from Products.Ploneboard.interfaces import IConversation
from Products.Ploneboard.interfaces import IForum
from Products.Ploneboard.permissions import AddComment
from Products.Ploneboard.permissions import EditComment
from Products.Ploneboard.permissions import ManageConversation
from Products.Ploneboard.permissions import MergeConversation
from Products.Ploneboard.permissions import ViewBoard
from zope import event
from zope.interface import implements
from zope.interface import Interface
from zope.interface import providedBy


PBConversationBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBConversationBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBConversationBaseBTreeFolderSchema['title'].write_permission = EditComment

schema = PBConversationBaseBTreeFolderSchema + Schema((
    TextField(
            'description',
            searchable=1,
            read_permission=ViewBoard,
            write_permission=EditComment,
            default_content_type='text/plain',
            default_output_type='text/plain',
            widget=TextAreaWidget(
                description="Enter a brief description of the conversation.",
                description_msgid="help_description_conversation",
                label="Description",
                label_msgid="label_description_conversation",
                i18n_domain="ploneboard",
                rows=5)
        ),
    ))
utils.finalizeSchema(schema)


class PloneboardConversation(BrowserDefaultMixin, BaseBTreeFolder):
    """Conversation contains comments."""

    implements(IConversation, INonStructuralFolder)
    meta_type = 'PloneboardConversation'
    schema = schema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    def _get_catalog(self):
        return api.portal.get_tool(name='portal_catalog')

    @security.protected(ManageConversation)
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    @security.protected(ViewBoard)
    def getTitle(self):
        """Get the title of this conversation"""
        return self.Title()

    @security.protected(ViewBoard)
    def getForum(self):
        """Returns containing forum."""
        # Try containment
        stoptypes = ['Plone Site']
        for obj in aq_chain(aq_inner(self)):
            if hasattr(obj, 'portal_type') and obj.portal_type not in stoptypes:
                if IForum.providedBy(obj):
                    return obj
        return None

    @security.protected(ManageConversation)
    def removeComment(self, comment):
        self.manage_delObjects([comment.getId()])
        # XXX reparent replies to this comment ?

    @security.protected(AddComment)
    def addComment(self, title, text, creator=None, files=None):
        """Adds a new comment with subject and body."""
        id = self.generateId(prefix='')
        if not title:
            title = self.Title()


        m = _createObjectByType('PloneboardComment', self, id)

        # XXX: There is some permission problem with AT write_permission
        # and using **kwargs in the _createObjectByType statement.
        m.setTitle(title)
        m.setText(text)
        if creator is not None:
            m.setCreators([creator])

        # Create files in message
        if files:
            for file in files:
                # Get raw filedata, not persistent object with reference to tempstorage
                attachment = File(file.getId(), file.title_or_id(), str(file.data), file.getContentType())
                m.addAttachment(attachment)

        # If this comment is being added by anonymous, make sure that the true
        # owner in zope is the owner of the forum, not the parent comment or
        # conversation. Otherwise, that owner may be able to view or delete
        # the comment.
        membership = api.portal.get_tool(name='portal_membership')
        if membership.isAnonymousUser():
            forum = self.getForum()
            utils.changeOwnershipOf(m, forum.owner_info()['id'], False)

        event.notify(ObjectInitializedEvent(m))
        m.indexObject()
        m.unmarkCreationFlag()
        self.reindexObject()  # Sets modified
        return m

    @security.protected(ViewBoard)
    def getComment(self, comment_id, default=None):
        """Returns the comment with the specified id."""
        # return self._getOb(comment_id, default)
        comments = self._get_catalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                getId=comment_id)
        if comments:
            return comments[0].getObject()
        else:
            return None

    @security.protected(ViewBoard)
    def getComments(self, limit=30, offset=0, **kw):
        """
        Retrieves the specified number of comments with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        query = {'object_provides' : 'Products.Ploneboard.interfaces.IComment',
                 'sort_on'           : 'created',
                 'sort_limit'        : (offset + limit),
                 'path'              : '/'.join(self.getPhysicalPath()), }
        query.update(kw)
        catalog = self._get_catalog()
        return [f.getObject() for f in catalog(**query)[offset:offset + limit]]

    @security.protected(ViewBoard)
    def getNumberOfComments(self):
        """
        Returns the number of comments in this conversation.
        """
        # XXX this was a portal_catalog search but as this method is used
        # by the index catalog.num_comments, there are problems when recataloging
        # as the sub elements are not returned and so
        # return len(self._get_catalog()(
        #    object_provides='Products.Ploneboard.interfaces.IComment',
        #    path='/'.join(self.getPhysicalPath())))
        membership = api.portal.get_tool(name='portal_membership')
        number = 0
        for comment in self.objectValues():
            if 'Products.Ploneboard.interfaces.IComment' in \
               [i.__identifier__ for i in providedBy(comment).flattened()] \
               and membership.checkPermission(View, comment):
                number = number + 1
        return number

    @security.protected(ViewBoard)
    def getLastCommentDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last comment
        for the conversation.
        """
        comment = self.getLastComment()
        if comment:
            return comment.created()
        return None

    @security.protected(ViewBoard)
    def getLastCommentAuthor(self):
        """
        Returns the name of the author of the last comment.
        """

        comment = self.getLastComment()
        if comment:
            return comment.Creator()
        return None

    security.declareProtected(ViewBoard, 'getLastCommentId')
    def getLastCommentId(self):
        """
        Returns the relative URL of the last comment
        for the conversation.
        """
        comment = self.getLastComment()
        if comment:
            return comment.getId()
        return None

    @security.protected(ViewBoard)
    def getLastComment(self):
        """
        Returns the last comment as full object..
        Returns None if there is no comment
        """

        res = self._get_catalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                sort_on='created',
                sort_order='reverse',
                sort_limit=1,
                path='/'.join(self.getPhysicalPath())
        )
        if res:
            return res[0].getObject()
        return None

    @security.protected(ViewBoard)
    def getRootComments(self):
        """
        Return a list all comments rooted to the board; ie comments which
        are not replies to other comments.
        """
        raw = self.getComments()
        ours = [ comment for comment in raw if comment.inReplyToUID() is None]
        ours = sorted(ours, key=lambda our: our.created())
        return ours

    @security.protected(ViewBoard)
    def getFirstComment(self):
        """
        See IConversation.getFirstComment.__doc__
        """
        res = self._get_catalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                sort_on='created', sort_limit=1,
                path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject()
        else:
            return None

    @security.protected(ManageConversation)
    def moveToForum(self, forum_id):
        """Moves conversation to another forum"""
        forum = self.getForum().getBoard().getForum(forum_id)
        if forum:
            parent = self.getForum()
            cut_objects = parent.manage_cutObjects((self.getId(),))
            forum.manage_pasteObjects(cut_objects)

    @security.protected(ManageConversation)
    def delete(self):
        """"""
        parent = self.getForum()
        parent._delObject(self.getId())

    @security.protected(ViewBoard)
    def Creator(self):
        # XXX Backwards compatability with old version
        return getattr(self, '_creator', None) or BaseBTreeFolder.Creator(self)

    def __nonzero__(self):
        return 1

    # No setting of default page - makes no sense
    def canSetDefaultPage(self):
        return False

    @security.protected(MergeConversation)
    def manage_pasteObjects(self, cp):
        """ merge another conversation """
        try:
            op, mdatas = _cb_decode(cp)
        except Exception:
            raise CopyError("Invalid content")
        if op == 0:
            raise ValueError('Not allowed to copy content into conversation')
        if op != 1:
            raise ValueError("Invalid operation of content")
        obj = self.unrestrictedTraverse(mdatas[0])
        if IConversation.providedBy(obj):
            if obj.getParentNode() != self.getParentNode():
                raise ValueError("Invalid parent of content")
            forum = obj.getForum()
            obj_id = obj.getId()
            o_list = obj.objectValues()
            oblist = [Moniker(o1).dump() for o1 in o_list]
            cp = (1, oblist)
            cp = _cb_encode(cp)
            CopyContainer.manage_pasteObjects(self, cp)
            forum.manage_delObjects([obj_id])
        elif IComment.providedBy(obj):
            return CopyContainer.manage_pasteObjects(self, cp)
        else:
            raise ValueError('Invalid type of content')


registerType(PloneboardConversation, PROJECTNAME)
