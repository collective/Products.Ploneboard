"""
$Id: PatchCatalogTool.py,v 1.2 2003/07/10 13:33:33 vladoi Exp $
"""

try:
    from Products.CMFCore.CatalogTool import CatalogTool
except ImportError:
    pass
else:
    if not hasattr(CatalogTool, '_old_listAllowedRolesAndUsers'):
        def _listAllowedRolesAndUsers(self, user):
            result = self._old_listAllowedRolesAndUsers(user)
            getGroups = getattr(user, 'getGroups', None)
            if getGroups is not None:
                for group in getGroups():
                    result.append('user:'+group)
            return result

        from zLOG import LOG, INFO
        LOG('GroupUserFolder', INFO, 'Patching CatalogTool')

        CatalogTool._old_listAllowedRolesAndUsers = CatalogTool._listAllowedRolesAndUsers
        CatalogTool._listAllowedRolesAndUsers = _listAllowedRolesAndUsers
