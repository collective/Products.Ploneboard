"""
$Id: PloneboardPermissions.py,v 1.2 2004/04/02 08:06:13 tesdal Exp $
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Ploneboard Permissions into one place
ViewBoard = 'Ploneboard: View'
SearchBoard = 'Ploneboard: Search'
AddBoard = 'Ploneboard: Add Ploneboard'
ManageBoard = 'Ploneboard: Add Ploneboard'
AddForum = 'Ploneboard: Add Forum'
ManageForum = 'Ploneboard: Add Forum'
AddConversation = 'Ploneboard: Add Conversation'
AddComment = 'Ploneboard: Add Comment'
EditComment = 'Ploneboard: Edit Comment'
AddAttachment = 'Ploneboard: Add Comment Attachment'
ManageConversation = 'Ploneboard: Manage Conversation'
ManageComment = 'Ploneboard: Manage Comment'
ApproveComment = 'Ploneboard: Approve Comment'

# Set up default roles for permissions
setDefaultRoles(ViewBoard,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(SearchBoard,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(AddBoard,
                ('Manager', 'Owner'))

setDefaultRoles(ManageBoard,
                ('Manager', 'Owner'))

setDefaultRoles(AddConversation,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(AddComment,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(EditComment,
                ('Manager',))

setDefaultRoles(AddAttachment,
                ('Manager',))

setDefaultRoles(ManageConversation,
                ('Manager', 'Reviewer'))

setDefaultRoles(ManageComment,
                ('Manager', 'Reviewer'))

setDefaultRoles(ApproveComment,
                ('Manager', 'Reviewer'))

