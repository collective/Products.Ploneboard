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

    qi_tool = getToolByName(portal, 'portal_quickinstaller')
    inst_vers = [prod['installedVersion'] for prod in qi_tool.listInstalledProducts() \
                 if prod['id'] == 'CMFMember']
    fs_vers = qi_tool.getProductVersion('CMFMember')
    
    if len(inst_vers) and inst_vers[0] != fs_vers:
        out.append('Reinstalling CMFMember Product')
        qi_tool.reinstallProducts(['CMFMember'])

    return out
