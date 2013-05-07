from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class SearchView(BrowserView):
    template = ViewPageTemplateFile("search.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        sp=getToolByName(context, "portal_properties").site_properties
        plone=getMultiAdapter((self.context, self.request), name="plone")

        def crop(text):
            return plone.cropText(text,
                    sp.search_results_description_length, sp.ellipsis)

        self.crop=crop
        self.normalize=getUtility(IIDNormalizer).normalize
        self.icons=plone.icons_visible()
        self.portal=getMultiAdapter((context, request),
                                    name="plone_portal_state").portal_url()+"/"


    def update(self):
        if "q" not in self.request.form:
            self.results=[]
            return

        text=self.request.form["q"]
        for char in [ "(", ")" ]:
            text=text.replace(char, '"%s"' % char)

        ct=getToolByName(self.context, "portal_catalog")
        self.results=ct(
                object_provides="Products.Ploneboard.interfaces.IComment",
               SearchableText=text)


    def info(self, brain):
        """Return display-information for a search result.
        """
        obj=brain.getObject()
        conv=obj.getConversation()
        forum=obj.getForum()
        # text=obj.Schema()["text"].get(obj, mimetype="text/plain").strip()
        text=obj.getText()

        return dict(
                author = brain.Creator,
                title = brain.Title,
                description = self.crop(text),
                url = brain.getURL()+"/view",
                icon = self.icons and self.portal+brain.getIcon or None,
                forum_url = forum.absolute_url(),
                forum_title = forum.title_or_id(),
                conv_url = conv.absolute_url(),
                conv_title = conv.title_or_id(),
                review_state = self.normalize(brain.review_state),
                portal_type = self.normalize(brain.portal_type),
                relevance = brain.data_record_normalized_score_)


    def board_url(self):
        state=getMultiAdapter((self.context, self.request), name="plone_context_state")
        return state.view_url()


    def __call__(self):
        self.update()
        return self.template()
