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

import GroupUserFolder
import GRUFFolder
from global_symbols import *

import AccessControl.User


##################################
## CMF / Plone SUPPORT START... ##
##################################

### Hotfix to let User objects support an 'id' method

##def fake_id(self,):
##    """faking the 'id' attribute for Owned.py module / ownerInfo method"""
##    Log(LOG_DEBUG, "Within fake_id")
##    return """__VERY_BAD_VALUE__"""

##def fake_getPhysicalRoot(self,):
##    try:
##        Log(LOG_DEBUG, "Within fake_getPhysicalRoot", self.getId(), self.getGRUFPhysicalRoot())
##        return self.getGRUFPhysicalRoot()
##    except:
##        Log(LOG_DEBUG, "Within fake_getPhysicalRoot", self.getId(), "but cannot access getGRUFPhysicalRoot()")
##        return None

##AccessControl.User.BasicUser.id = fake_id
##AccessControl.User.BasicUser.getPhysicalRoot = fake_getPhysicalRoot

##################################
##  CMF / Plone SUPPORT END...  ##
##################################

Log(LOG_NOTICE, "Loaded GroupUserFolder.")


def initialize(context):
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


    
