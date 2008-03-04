from Acquisition import aq_inner
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class RSSView(BrowserView):
    template = ZopeTwoPageTemplateFile("rss.pt")

    def __init__(self, context, request):
        super(RSSView, self).__init__(context, request)
        self.response=request.response
        self.context_state=getMultiAdapter((context, request),
                                           name="plone_context_state")
        sp=getToolByName(context, "portal_properties").site_properties
        plone_view=getMultiAdapter((context, request), name="plone")
        def crop(text):
            return plone_view.cropText(text,
                    sp.search_results_description_length, sp.ellipsis)
        self.crop=crop
        self.formatTime=plone_view.toLocalizedTime
        self.syndication=getToolByName(context, "portal_syndication")


    def updatePeriod(self):
        return self.syndication.getUpdatePeriod(aq_inner(self.context))


    def updateFrequency(self):
        return self.syndication.getUpdateFrequency(aq_inner(self.context))


    def updateBase(self):
        return self.syndication.getHTML4UpdateBase(aq_inner(self.context))


    def title(self):
        return self.context_state.object_title()


    def description(self):
        return self.context.Description()


    def url(self):
        return self.context_state.view_url()


    def date(self):
        return self.context.modified().HTML4()


    def _morph(self, brain):
        obj=brain.getObject()
        text=obj.Schema()["text"].get(obj, mimetype="text/plain").strip()

        return dict(
                title = brain.Title,
                url = brain.getURL()+"/view",
                description = self.crop(text),
                date = brain.created.HTML4(),
                author = brain.Creator,
                )


    def update(self):
        catalog=getToolByName(self.context, "portal_catalog")
        query=dict(
                path="/".join(aq_inner(self.context).getPhysicalPath()),
                object_provides="Products.Ploneboard.interfaces.IComment",
                sort_on="created",
                sort_order="reverse",
                sort_limit=20)
        brains=catalog(query)
        self.comments=[self._morph(brain) for brain in brains]


    def __call__(self):
        if not self.syndication.isSyndicationAllowed(aq_inner(self.context)):
            raise Unauthorized, "Syndication is not enabled"
        self.update()
        self.response.setHeader("Content-Type", "text/xml;charset=utf-8")
        return self.template()



