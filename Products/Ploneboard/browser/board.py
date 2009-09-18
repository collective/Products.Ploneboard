from Products import Five
from Products.Ploneboard.browser.utils import toPloneboardTime

class BoardView(Five.BrowserView):
    """View methods for board type
    """

    def __init__(self, context, request):
        Five.BrowserView.__init__(self, context, request)

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        return toPloneboardTime(self.context, self.request, time_)
