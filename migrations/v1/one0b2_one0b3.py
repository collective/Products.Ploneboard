from Products.CMFCore.utils import getToolByName
from Products.CMFMember.utils import _MethodWrapper, userFolderDelUsers

def oneZeroBeta3(portal):
    """ upgrade from CMFMember 1.0 beta2 to CMFMember 1.0 beta3 """
    out = []

    #Override user deletion method in acl_users to ensure member objects
    #always get deleted
    out.append('Patching acl_users userFolderDelUsers() method')
    acl_users = getToolByName(portal, 'acl_users')
    acl_users.userFolderDelUsers = _MethodWrapper(userFolderDelUsers)

    #trigger the setDefaultType() method to ensure that the defaultMemberSchema
    #class variable gets set correctly
    out.append('Triggering correct default member schema storage')
    md_tool = getToolByName(portal, 'portal_memberdata')
    md_tool.setDefaultType(md_tool.getTypeName())

    return out
