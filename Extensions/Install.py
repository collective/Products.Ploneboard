from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CompositePack.config import PROJECTNAME, GLOBALS, TOOL_ID
from Products.CompositePack.config import COMPOSABLE, COMPOSABLE_TYPES 
from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool
from StringIO import StringIO

KUPU_TOOL_ID = PloneKupuLibraryTool.id

def install_tool(self, out):
      if hasattr(self, TOOL_ID):
          uninstall(self, out)
      self.manage_addProduct['CompositePack'].manage_addCompositeTool()
      out.write("CompositePack Tool Installed")
        
def install_kupu_resource(self, out):
      if hasattr(self, KUPU_TOOL_ID):
          kupu_tool = getattr(self, KUPU_TOOL_ID)
          kupu_tool.addResourceType(COMPOSABLE, COMPOSABLE_TYPES)
          out.write("Composable Resource created in Kupu Library Tool")
      else:
          out.write("Kupu Library Tool not available")
        
def uninstall_tool(self, out):
    self.manage_delObjects(ids=[TOOL_ID,])
    out.write("CompositePack Tool UnInstalled")

def uninstall_kupu_resource(self, out):
      if hasattr(self, KUPU_TOOL_ID):
          kupu_tool = getattr(self, KUPU_TOOL_ID)
          kupu_tool.deleteResourceTypes([COMPOSABLE])
          out.write("Composable Resource deleted in Kupu Library Tool")
      else:
          out.write("Kupu Library Tool not available")
        
def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    
    install_tool(self, out)
    
    install_kupu_resource(self, out)
    
    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
    
def uninstall(self):
    out = StringIO()
    uninstall_tool(self, out)
    uninstall_kupu_resource(self, out)
    out.write("Successfully uninstalled %s." % PROJECTNAME)
    return out.getvalue()
