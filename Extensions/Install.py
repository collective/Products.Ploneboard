from Products.CMFTypes.debug import log, log_exc
from Products.CMFTypes.ExtensibleMetadata import ExtensibleMetadata
from Products.CMFTypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

from Products.CMFMember import GLOBALS, PKG_NAME, SKIN_NAME
from Products.CMFMember import listTypes



def installMember(self, out):
    installTypes(self, out, listTypes(PKG_NAME), PKG_NAME)

def replaceTools(self, out):
    try:
        self.manage_delObjects(['portal_memberdata'])
    except:
        pass
    
    addTool = self.manage_addProduct[PKG_NAME].manage_addTool
    addTool('MemberDataTool', None)
    
def install(self):
    out=StringIO()
    
    installMember(self, out)
    replaceTools(self, out)
    
    print >> out, 'Successfully installed %s' % PKG_NAME
    return out.getvalue()
