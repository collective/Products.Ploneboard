##############################################################################
#
# Copyright (c) 2003 Connexions Projects and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic usergroup tool.

$Id: GroupsToolPermissions.py,v 1.2 2003/09/23 19:45:42 jccooper Exp $
"""

from Products.CMFCore.CMFCorePermissions import setDefaultRoles

#AddRisaModuleEditor = 'Add RISA Module Editor'
#setDefaultRoles(AddRisaModuleEditor, ('Manager', 'Owner', 'Member', 'Anonymous'))

ManageGroups = 'Manage Groups'
setDefaultRoles(ManageGroups, ('Manager',))

ViewGroups = 'View Groups'
setDefaultRoles(ViewGroups, ('Manager', 'Owner', 'Member'))

SetGroupOwnership = 'Set Group Ownership'
setDefaultRoles(SetGroupOwnership, ('Manager', 'Owner'))