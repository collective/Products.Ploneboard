from Products import Five
from Products.Ploneboard.browser.utils import toPloneboardTime

class ForumView(Five.BrowserView):
    """View methods for forum type
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        return toPloneboardTime(self.context, self.request, time_)
