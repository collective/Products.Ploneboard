##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL
#
##############################################################################

"""GroupUserFolder product"""

import GroupUserFolder
import GRUFFolder
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
