"""
$Id: PatchCatalogTool.py,v 1.1 2003/07/10 10:20:32 vladoi Exp $
"""

from zLOG import LOG, INFO
from Products.CMFCore.CatalogTool import CatalogTool

if not hasattr(CatalogTool, '_old_listAllowedRolesAndUsers'):
    def _listAllowedRolesAndUsers(self, user):
        result = self._old_listAllowedRolesAndUsers(user)
        getGroups = getattr(user, 'getGroups', None)
        if getGroups is not None:
            for group in getGroups():
                result.append('user:'+group)
        return result

    LOG('GroupUserFolder', INFO, 'Patching CatalogTool')

    CatalogTool._old_listAllowedRolesAndUsers = CatalogTool._listAllowedRolesAndUsers
    CatalogTool._listAllowedRolesAndUsers = _listAllowedRolesAndUsers
