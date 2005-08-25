from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.permissions import setDefaultRoles


# Gathering Ploneboard Permissions into one place

# Add permissions differ for each type, and are imported by __init__.initialize
# so don't change their names!
ViewBoard = 'Ploneboard: View'
SearchBoard = 'Ploneboard: Search'
AddBoard = AddPloneboard = 'Ploneboard: Add Ploneboard'
ManageBoard = 'Ploneboard: Add Ploneboard'
AddForum = AddPloneboardForum = 'Ploneboard: Add Forum'
ManageForum = 'Ploneboard: Add Forum'
AddConversation = AddPloneboardConversation = 'Ploneboard: Add Conversation'
AddComment = AddPloneboardComment = 'Ploneboard: Add Comment'
EditComment = 'Ploneboard: Edit Comment'
AddAttachment = AddPloneboardAttachment = 'Ploneboard: Add Comment Attachment'
ManageConversation = 'Ploneboard: Manage Conversation'
ManageComment = 'Ploneboard: Manage Comment'
ApproveComment = 'Ploneboard: Approve Comment'
# XXX This next permission can probably be removed.
NotifyRetracted = 'Ploneboard: Notify Retracted'

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
setDefaultRoles(NotifyRetracted,
                ('Manager', 'Reviewer', 'Owner'))

