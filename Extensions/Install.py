from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

_globals = globals()

def install_tools(self, out):
    if not hasattr(self, "portal_squid"):
        addTool = self.manage_addProduct['CMFSquidTool'].manage_addTool
        addTool('CMF Squid Tool')

def install(self):
    out = StringIO()
    print >>out, "Installing CMFSquidTool"

    install_tools(self, out)
    return out.getvalue()


