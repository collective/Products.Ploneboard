from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CompositePack.config import PROJECTNAME, GLOBALS, TOOL_ID
from Products.CompositePack.config import COMPOSABLE, COMPOSABLE_TYPES 
from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool
from StringIO import StringIO

KUPU_TOOL_ID = PloneKupuLibraryTool.id

COMPO_TYPE = 'CMF Composite Page'

def install_tool(self, out):
    if hasattr(self, TOOL_ID):
      uninstall_tool(self, out)
    self.manage_addProduct['CompositePack'].manage_addCompositeTool()
    out.write("CompositePack Tool Installed")

def set_hidden_type_from_navtree(self, out):    
    metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
    if not COMPO_TYPE in metaTypesNotToList:
        metaTypesNotToList.append(COMPO_TYPE)
        self.portal_properties.navtree_properties.metaTypesNotToList = metaTypesNotToList
    out.write("CMF Composite Page hidden in navigation tree")
        
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

def unset_hidden_type_from_navtree(self, out):    
    metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
    if COMPO_TYPE in metaTypesNotToList:
        metaTypesNotToList.remove(COMPO_TYPE)
        self.portal_properties.navtree_properties.metaTypesNotToList = metaTypesNotToList
    out.write("CMF Composite Page hidden in navigation tree")

def uninstall_kupu_resource(self, out):
      if hasattr(self, KUPU_TOOL_ID):
          kupu_tool = getattr(self, KUPU_TOOL_ID)
          try:
              kupu_tool.deleteResourceTypes([COMPOSABLE])
              out.write("Composable Resource deleted in Kupu Library Tool")
          except KeyError:
              pass
      else:
          out.write("Kupu Library Tool not available")
        
def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    set_hidden_type_from_navtree(self, out)

    install_subskin(self, out, GLOBALS)
    
    install_tool(self, out)
    
    install_kupu_resource(self, out)
    
    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
    
def uninstall(self):
    out = StringIO()
    unset_hidden_type_from_navtree(self, out)
    uninstall_tool(self, out)
    uninstall_kupu_resource(self, out)
    out.write("Successfully uninstalled %s." % PROJECTNAME)
    return out.getvalue()
