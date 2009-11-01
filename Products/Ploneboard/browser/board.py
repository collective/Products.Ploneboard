from Products import Five
from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.browser.utils import toPloneboardTime, getNumberOfConversations
from Products.Ploneboard.interfaces import IForum, IComment

class BoardView(Five.BrowserView):
    """View methods for board type
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

    def getKeyedForums(self, sitewide=False):
        """Return all the forums in a board."""
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'object_provides':IForum.__identifier__}
        if not sitewide:
            query['path'] = '/'.join(self.context.getPhysicalPath())

        result = {}

        for f in catalog(query):
            obj = f._unrestrictedGetObject()
            data = dict(absolute_url=f.getURL(),
                        Title=f.Title,
                        Description=f.Description,
                        getNumberOfConversations=getNumberOfConversations(obj, catalog), # XXX THIS AND CATEGORY IS WHY WE NEED GETOBJECT, TRY CACHING
                        getLastCommentDate=None,
                        getLastCommentAuthor=None,
                        )

            lastcomment = catalog(object_provides=IComment.__identifier__,
                                  sort_on='created',
                                  sort_order='reverse',
                                  sort_limit=1,
                                  path='/'.join(obj.getPhysicalPath()))
            if lastcomment:
                lastcomment = lastcomment[0]
                data['getLastCommentDate'] = self.toPloneboardTime(lastcomment.created)
                data['getLastCommentAuthor'] = lastcomment.Creator


            try:
                categories = obj.getCategory()
            except AttributeError:
                categories = None
            if not categories:
                categories = None
            if not isinstance(categories, (tuple,list)):
                categories = categories,
            for category in categories:
                try:
                    categoryforums = result.get(category, [])
                    categoryforums.append(data)
                    result[category] = categoryforums
                except TypeError: # category is list?!
                    result[', '.join(category)] = data
        return result

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        return toPloneboardTime(self.context, self.request, time_)
