from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CompositePack.config import PROJECTNAME, GLOBALS, TOOL_ID

from StringIO import StringIO

def install_tool(self, out):
      if hasattr(self, TOOL_ID):
          uninstall(self, out)
      self.manage_addProduct['CompositePack'].manage_addCompositeTool()
      out.write("CompositePack Tool Installed")
        
def uninstall_tool(self, out):
    self.manage_delObjects(ids=[TOOL_ID,])
    out.write("CompositePack Tool UnInstalled")

def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    
    install_tool(self, out)

    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
    
def uninstall(self):
    out = StringIO()
    uninstall_tool(self, out)
    out.write("Successfully uninstalled %s." % PROJECTNAME)
    return out.getvalue()
