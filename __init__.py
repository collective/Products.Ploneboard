##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Ingeniweb SARL
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""GroupUserFolder product"""

import PatchCatalogTool
import GroupUserFolder
import GRUFFolder
from global_symbols import *
from Products.CMFCore.DirectoryView import registerDirectory
import AccessControl.User

global groupuserfolder_globals
groupuserfolder_globals=globals()



def initialize(context):

    registerDirectory('skins', groupuserfolder_globals)
    
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
        from Products.CMFCore.utils import ToolInit
        from GroupsTool import GroupsTool
        from GroupDataTool import GroupDataTool
        ToolInit( meta_type='CMF Groups Tool'
                  , tools=( GroupsTool, GroupDataTool, )
                  , product_name='GroupUserFolder'
                  , icon="tool.gif"
                  ).initialize( context )
    except ImportError:
        Log(LOG_NOTICE, "Unable to import GroupsTool and/or GroupDataTool (see exception in the log below)")
        LogException()
    
