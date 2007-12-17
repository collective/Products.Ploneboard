from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
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

class Assignment(base.Assignment):
    implements(IRecentConversationsPortlet)

    title = _(u"box_recent_conversations", "Recent conversations")


class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

    @memoize
    def results(self, limit=5):
        wt=getToolByName(self.context, "portal_workflow")
        ct=getToolByName(self.context, "portal_catalog")
        normalize=getUtility(IIDNormalizer).normalize
        icons=getMultiAdapter((self.context, self.request),
                                name="plone_view").icons_visible()
        if icons:
            portal=getMultiAdapter((self.context, self.request),
                                    name="plone_portal_state").portal_url()+"/"
        brains=ct(
                object_provides="Products.Ploneboard.interfaces.IConversation",
                sort_on="modified",
                sort_order="reverse",
                sort_limit=limit)[:limit]

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
                    portal_type = normalize(brain.portal_type))

        return [morph(brain) for brain in brains]

    @property
    def available(self):
        return len(self.results())>0

    def update(self):
        self.conversations=self.results()

    @property
    def next_url(self):
        state=getMultiAdapter((self.context, self.request),
                                name="plone_portal_state")
        return state.portal_url()+"/ploneboard_recent"

    render = ViewPageTemplateFile("recent.pt")

class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()

