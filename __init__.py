##############################################################################
#
# Copyright (c) 2002-2004+ Ingeniweb SARL
#
##############################################################################

"""GroupUserFolder product"""

import GroupUserFolder
import GRUFFolder
try:
    import Products.LDAPUserFolder
    hasLDAP = 1
except ImportError:
    hasLDAP = 0
from global_symbols import *

# Plone import try/except
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    import GroupsToolPermissions
except:
    # No registerdir available -> we ignore
    pass



# Used in Extension/install.py
global groupuserfolder_globals
groupuserfolder_globals=globals()


# LDAPUserFolder patching
if hasLDAP:
    import LDAPGroupFolder
    
    def patch_LDAPUF():
        # Now we can patch LDAPUF
        from Products.LDAPUserFolder import LDAPUserFolder
        import LDAPUserFolderAdapter
        LDAPUserFolder._doAddUser = LDAPUserFolderAdapter._doAddUser
        LDAPUserFolder._doDelUsers = LDAPUserFolderAdapter._doDelUsers
        LDAPUserFolder._doChangeUser = LDAPUserFolderAdapter._doChangeUser
        LDAPUserFolder._find_user_dn = LDAPUserFolderAdapter._find_user_dn
        LDAPUserFolder.manage_editGroupRoles = LDAPUserFolderAdapter.manage_editGroupRoles
        LDAPUserFolder._mangleRoles = LDAPUserFolderAdapter._mangleRoles

    # Patch LDAPUF  : XXX FIXME: have to find something cleaner here?
    patch_LDAPUF()


def initialize(context):

    try:
        registerDirectory('skins', groupuserfolder_globals)
    except:
        # No registerdir available => we ignore
        pass

    context.registerClass(
        GroupUserFolder.GroupUserFolder,
        permission='Add GroupUserFolders',
        constructors=(GroupUserFolder.manage_addGroupUserFolder,),
        icon='www/GroupUserFolder.gif',
        )

    if hasLDAP:
        context.registerClass(
            LDAPGroupFolder.LDAPGroupFolder,
            permission='Add GroupUserFolders',
            constructors=(LDAPGroupFolder.addLDAPGroupFolderForm, LDAPGroupFolder.manage_addLDAPGroupFolder,),
            icon='www/GroupUserFolder.gif',
            )


    context.registerClass(
        GRUFFolder.GRUFUsers,
        permission='Add GroupUserFolder',
        constructors=(GRUFFolder.manage_addGRUFUsers,),
        visibility=None,
        icon='www/GRUFUsers.gif',
        )

    context.registerClass(
        GRUFFolder.GRUFGroups,
        permission='Add GroupUserFolder',
        constructors=(GRUFFolder.manage_addGRUFGroups,),
        visibility=None,
        icon='www/GRUFGroups.gif',
        )

    try:
        from Products.CMFCore.utils import ToolInit, ContentInit
        from GroupsTool import GroupsTool
        from GroupDataTool import GroupDataTool
        ToolInit( meta_type='CMF Groups Tool'
                  , tools=( GroupsTool, GroupDataTool, )
                  , product_name='GroupUserFolder'
                  , icon="tool.gif"
                  ).initialize( context )

    except ImportError:
        Log(LOG_NOTICE, "Unable to import GroupsTool and/or GroupDataTool. \
        This won't disable GRUF but if you use CMF/Plone you won't get benefit of its special features.")
