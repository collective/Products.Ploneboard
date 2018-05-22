from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain
from Acquisition import aq_inner
from OFS.CopySupport import CopyContainer
from OFS.Image import File
from plone import api
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import BaseBTreeFolder
from Products.Archetypes.public import BaseBTreeFolderSchema
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import IntDisplayList
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.CMFPlone.interfaces import INonStructuralFolder \
    as ZopeTwoINonStructuralFolder
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import _createObjectByType, log_deprecated
from Products.Ploneboard import utils
from Products.Ploneboard.config import PROJECTNAME, HAS_SIMPLEATTACHMENT
from Products.Ploneboard.interfaces import IComment
from Products.Ploneboard.interfaces import IConversation
from Products.Ploneboard.interfaces import IForum
from Products.Ploneboard.interfaces import IPloneboard
from Products.Ploneboard.permissions import AddConversation
from Products.Ploneboard.permissions import ManageForum
from Products.Ploneboard.permissions import MoveConversation
from Products.Ploneboard.permissions import ViewBoard
from zope import event
from zope.interface import implementer
from zope.interface import Interface

_ = utils.PloneboardMessageFactory

AttachmentSizes = IntDisplayList((
        (10, _(u'10 kilobyte')),
        (100, _(u'100 kilobyte')),
        (1000, _(u'1 megabyte')),
        (10000, _(u'10 megabyte')),
        (-1, _(u'unlimited')),
   ))

schema = BaseBTreeFolderSchema + Schema((
    TextField('description',
        searchable=1,
        default_content_type='text/html',
        default_output_type='text/plain',
        widget=TextAreaWidget(
            description="Brief description of the forum topic.",
            description_msgid="help_description_forum",
            label="Description",
            label_msgid="label_description_forum",
            i18n_domain="ploneboard",
            rows=5
        )
    ),
    LinesField('category',
         write_permission=ManageForum,
         vocabulary='getCategories',
         widget=MultiSelectionWidget(
            description="Select which category the forum should be listed "
                        "under. A forum can exist in multiple categories, "
                        "although using only one category is recommended.",
            description_msgid="help_category",
            condition="object/getCategories",
            label="Category",
            label_msgid="label_category",
            i18n_domain="ploneboard",
          )
    ),
    IntegerField('maxAttachments',
        write_permission=ManageForum,
        default=1,
        widget=IntegerWidget(
             description="Select the maximum number of attachments per comment.",
             description_msgid="help_maxattachments",
             label="Maximum number of attachments",
             label_msgid="label_maxattachments",
             i18n_domain="ploneboard",
        )
    ),
    IntegerField('maxAttachmentSize',
        write_permission=ManageForum,
        vocabulary=AttachmentSizes,
        default=100,
        widget=SelectionWidget(
             description="Select the maximum size for attachments.",
             description_msgid="help_maxattachmentsize",
             label="Maximum attachment size",
             label_msgid="label_maxattachmentsize",
             i18n_domain="ploneboard",
        )
    ),
    BooleanField('allowEditComment',
        default=False,
        languageIndependent=0,
        widget=BooleanWidget(
            label=u'Allow users to edit their comments',
            description=u'If selected, this will give users the ability to '
                        u'edit their own comments.',
            label_msgid='label_allow_edit_comment',
            description_msgid='help_allow_edit_comment',
            # Only show when no conversations exist
            condition="not:object/getNumberOfConversations|nothing",
            ),
    ),
    BooleanField(
        'showCaptcha',
        write_permission=ManageForum,
        default=False,
        widget=BooleanWidget(
            description=_(
                u'help_showcaptcha',
                default=u'Select if show or not captcha for anonymous (if '
                        u'recaptcha installed and configured).'),
            label=_(u'label_show_captcha', default=u"Show Captcha"),
        )),
))
utils.finalizeSchema(schema)


if not HAS_SIMPLEATTACHMENT:
    schema['maxAttachments'].mode = "r"
    schema['maxAttachments'].default = 0
    schema['maxAttachments'].widget.visible = {
        'edit' : 'invisible',
        'view' : 'invisible'
    }
    schema['maxAttachmentSize'].widget.visible = {
        'edit' : 'invisible',
        'view' : 'invisible'
    }


@implementer(IForum, INonStructuralFolder)
class PloneboardForum(BaseBTreeFolder):
    """A Forum contains conversations."""

    meta_type = 'PloneboardForum'
    schema = schema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    def _get_catalog(self):
        return api.portal.get_tool(name='portal_catalog')

    @security.protected(ManageForum)
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    @security.public
    def synContentValues(self):
        return (self.getConversations())

    @security.protected(ViewBoard)
    def getBoard(self):
        """Returns containing or nearest board."""
        # Try containment
        stoptypes = ['Plone Site']
        for obj in aq_chain(aq_inner(self)):
            if hasattr(obj, 'portal_type') and obj.portal_type not in stoptypes:
                if IPloneboard.providedBy(obj):
                    return obj

        return None

    @security.protected(AddConversation)
    def addConversation(self, title, text=None, creator=None, files=None,
                        conversation_type='PloneboardConversation',
                        **kwargs):
        """Adds a new conversation to the forum.

        XXX should be possible to parameterise the exact type that is being
        added.
        """

        id = self.generateId(prefix='')

        conv = _createObjectByType(conversation_type, self, id)

        # XXX: There is some permission problem with AT write_permission
        # and using **kwargs in the _createObjectByType statement.
        conv.setTitle(title)
        for fieldname, value in kwargs.items():
            conv.getField(fieldname).getMutator(conv)(value)

        if creator is not None:
            conv.setCreators([creator])

        event.notify(ObjectInitializedEvent(conv))
        if text is not None or files:
            m = _createObjectByType(
                'PloneboardComment',
                conv,
                conv.generateId(prefix='')
            )

            # XXX: There is some permission problem with AT write_permission
            # and using **kwargs in the _createObjectByType statement.
            m.setTitle(title)
            if text is not None:
                m.setText(text)

            if creator is not None:
                m.setCreators([creator])

            # Create files in message
            for file in files or []:
                # Get raw filedata, not persistent object with reference to
                # tempstorage
                attachment = File(
                    file.getId(),
                    file.title_or_id(),
                    str(file.data),
                    file.getContentType()
                )
                m.addAttachment(attachment)

            event.notify(ObjectInitializedEvent(m))
            m.reindexObject()
            m.unmarkCreationFlag()
        conv.reindexObject()
        return conv

    @security.protected(ViewBoard)
    def getConversation(self, conversation_id, default=None):
        """Returns the conversation with the given conversation id."""
        # return self._getOb(conversation_id, default)
        catalog = self._get_catalog()
        conversations = catalog(
                object_provides=IConversation.__identifier__,
                getId=conversation_id,
                path='/'.join(self.getPhysicalPath()))
        if conversations:
            return conversations[0].getObject()
        else:
            return None

    @security.protected(ManageForum)
    def removeConversation(self, conversation_id):
        """Removes a conversation with the given conversation id from the
        forum.
        """
        self._delObject(conversation_id)

    @security.protected(ViewBoard)
    def getConversations(self, limit=20, offset=0):
        """Returns conversations."""
        log_deprecated(
            'Products.Ploneboard.content.PloneboardForum.'
            'PloneboardForum.getConversations is deprecated in favor of '
            'Products.Ploneboard.browser.forum.ForumView.getConversations'
        )
        catalog = self._get_catalog()
        brains = catalog(
            object_provides=IConversation.__identifier__,
            sort_on='modified',
            sort_order='reverse',
            sort_limit=(offset + limit),
            path='/'.join(self.getPhysicalPath())
        )
        return [f.getObject() for f in brains[offset:offset + limit]]


    @security.protected(ViewBoard)
    def getNumberOfConversations(self):
        """Returns the number of conversations in this forum."""
        log_deprecated("Products.Ploneboard.content.PloneboardForum."
                       "PloneboardForum.getNumberOfConversations is "
                       "deprecated in favor of Products.Ploneboard.browser."
                       "forum.ForumView.getNumberOfConversations"
        )
        return len(
            self._get_catalog()(
                object_provides=IConversation.__identifier__,
                path='/'.join(self.getPhysicalPath())
            )
        )

    @security.protected(ViewBoard)
    def getNumberOfComments(self):
        """Returns the number of comments to this forum."""
        log_deprecated(
            "Products.Ploneboard.content.PloneboardForum."
            "PloneboardForum.getNumberOfComments is deprecated in favor of "
            "Products.Ploneboard.browser.forum.ForumView.getNumberOfComments"
        )
        return len(self._get_catalog()(
            object_provides='Products.Ploneboard.interfaces.IComment',
            path='/'.join(self.getPhysicalPath())))

    @security.protected(ViewBoard)
    def getLastConversation(self):
        """
        Returns the last conversation.
        """
        # XXX Is Created or Modified the most interesting part?
        res = self._get_catalog()(
                object_provides=IConversation.__identifier__,
                sort_on='created', sort_order='reverse', sort_limit=1,
                path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject()

    @security.protected(ViewBoard)
    def getLastCommentDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last comment
        for the forum.
        """
        res = self._get_catalog()(
            object_provides='Products.Ploneboard.interfaces.IComment',
            sort_on='created', sort_order='reverse', sort_limit=1,
            path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].created

    @security.protected(ViewBoard)
    def getLastCommentAuthor(self):
        """
        Returns the name of the author of the last comment.
        """
        res = self._get_catalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                sort_on='created', sort_order='reverse', sort_limit=1,
                path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].Creator
        else:
            return None

    # Vocabularies
    @security.protected(ViewBoard)
    def getCategories(self):
        value = []
        board = self.getBoard()
        if board is not None and hasattr(board, 'getCategories'):
            categories = board.getCategories()
            if categories is not None:
                value = [(c, c) for c in categories]
        value.sort()
        return DisplayList(value)

    @security.protected(ViewBoard)
    def getAttachmentSizes(self):
        voc = DisplayList()
        voc.add('10', '10 kilobyte')
        voc.add('100', '100 kilobyte')
        voc.add('1000', '1 megabyte')
        voc.add('10000', '10 megabyte')
        voc.add('-1', 'unlimited')
        return voc

    @security.public
    def getConversationBatchSize(self):
        pb_tool = api.portal.get_tool(name='portal_ploneboard')
        prop_name = "%s_ConversationBatchSize" % self.getId()
        if pb_tool.hasProperty(prop_name):
            return pb_tool.getProperty(prop_name)
        prop_name = "ConversationBatchSize"
        if pb_tool.hasProperty(prop_name):
            return pb_tool.getProperty(prop_name)
        return 30


    ############################################################################
    # Folder methods, indexes and such

    @security.protected(MoveConversation)
    def manage_pasteObjects(self, cp):
        """ move another conversation """
        CopyContainer.manage_pasteObjects(self, cp)

    def __nonzero__(self):
        return 1


registerType(PloneboardForum, PROJECTNAME)
