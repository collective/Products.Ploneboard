##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL
#
# This software is subject to the provisions of the GNU Public License,
# Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
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


# Plone2 import try/except
IS_PLONE2 = 0
try:
    import Products.CMFFormController
    IS_PLONE2 = 1
except:
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
        if IS_PLONE2:
            Log(LOG_DEBUG, "Using Plone2's GroupSpace feature")
            import GroupSpace
            ContentInit(
                'The GroupSpace content type',
                content_types = (GroupSpace.GroupSpace, ),
                permission = GroupSpace.GroupSpace_addPermission,
                extra_constructors = (GroupSpace.addGroupSpace, ),
                fti = (GroupSpace.factory_type_information,),
                ).initialize(context)
            
    except ImportError:
        Log(LOG_NOTICE, "Unable to import GroupsTool and/or GroupDataTool. \
        This won't disable GRUF but if you use CMF/Plone you won't get benefit of its special features.")
    
