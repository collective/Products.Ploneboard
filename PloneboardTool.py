from AccessControl import ClassSecurityInfo
import Globals
from OFS.Folder import Folder
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from PloneboardPermissions import AddAttachment

class PloneboardTool(UniqueObject, Folder, ActionProviderBase):
    id = 'portal_ploneboard'
    meta_type = 'Ploneboard Tool'
    
    security = ClassSecurityInfo()
    
Globals.InitializeClass(PloneboardTool)
