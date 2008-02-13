from zope.interface import implements
from zope import schema
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.formlib.form import Fields
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Ploneboard.utils import PloneboardMessageFactory as _


class IRecentConversationsPortlet(IPortletDataProvider):
    """A portlet which shows recent Ploneboard conversations.
    """

    title = schema.TextLine(title=_(u"title_title",
                                default=u"Portlet title"),
                        required=True,
                        default=u"Recent messages")

    count = schema.Int(title=_(u"title_count",
                                default=u"Number of items to display"),
                       description=_(u"help_count",
                                default=u"How many items to list."),
                       required=True,
                       default=5)


class Assignment(base.Assignment):
    implements(IRecentConversationsPortlet)

    title = u"Recent messages"
    count = 5

    def __init__(self, title=None, count=None):
        if title is not None:
            self.title=title
        if count is not None:
            self.count=count


class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

    @memoize
    def results(self):
        ct=getToolByName(self.context, "portal_catalog")
        normalize=getUtility(IIDNormalizer).normalize
        icons=getMultiAdapter((self.context, self.request),
                                name="plone").icons_visible()
        if icons:
            portal=getMultiAdapter((self.context, self.request),
                                    name="plone_portal_state").portal_url()+"/"
        brains=ct(
                object_provides="Products.Ploneboard.interfaces.IConversation",
                sort_on="modified",
                sort_order="reverse",
                sort_limit=self.data.count)[:self.data.count]

        def morph(brain):
            obj=brain.getObject()
            forum=obj.getForum()

            return dict(
                    title = brain.Title,
                    description = brain.Description,
                    url = brain.getURL()+"/view",
                    icon = icons and portal+brain.getIcon or None,
                    forum_url = forum.absolute_url(),
                    forum_title = forum.title_or_id(),
                    review_state = normalize(brain.review_state),
                    portal_type = normalize(brain.portal_type),
                    date = brain.modified)

        return [morph(brain) for brain in brains]

    @property
    def available(self):
        return len(self.results())>0

    def update(self):
        self.conversations=self.results()

    @property
    def title(self):
        return self.data.title

    @property
    def next_url(self):
        state=getMultiAdapter((self.context, self.request),
                                name="plone_portal_state")
        return state.portal_url()+"/ploneboard_recent"

    render = ViewPageTemplateFile("recent.pt")


class AddForm(base.AddForm):
    form_fields = Fields(IRecentConversationsPortlet)
    label = _(u"label_add_portlet",
                default=u"Add recent conversations portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows conversations with recent comments.")

    def create(self, data):
        return Assignment(title=data.get("title"), count=data.get("count"))


class EditForm(base.EditForm):
    form_fields = Fields(IRecentConversationsPortlet)
    label = _(u"label_add_portlet",
                default=u"Add recent conversations portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows conversations with recent comments.")

