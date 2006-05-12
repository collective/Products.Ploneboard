from Products.CMFCore import permissions
from Products.CMFCore.permissions import setDefaultRoles


# Gathering Ploneboard Permissions into one place
RequestReview = permissions.RequestReview
# Add permissions differ for each type, and are imported by __init__.initialize
# so don't change their names!

# Separate view permission creates havoc
#ViewBoard = 'Ploneboard: View'
ViewBoard = permissions.View
SearchBoard = 'Ploneboard: Search'
AddBoard = AddPloneboard = 'Ploneboard: Add Ploneboard'
ManageBoard = 'Ploneboard: Add Ploneboard'


AddForum = AddPloneboardForum = 'Ploneboard: Add Forum'
ManageForum = 'Ploneboard: Add Forum'

AddConversation = AddPloneboardConversation = 'Ploneboard: Add Conversation'
ManageConversation = 'Ploneboard: Manage Conversation'

AddComment = AddPloneboardComment = 'Ploneboard: Add Comment'
EditComment = 'Ploneboard: Edit Comment'
ViewComment = 'Ploneboard: View Comment'

AddAttachment = AddPloneboardAttachment = 'Ploneboard: Add Comment Attachment'
ManageComment = 'Ploneboard: Manage Comment'
ApproveComment = 'Ploneboard: Approve Comment' # Used for moderation


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

setDefaultRoles(ViewComment,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(AddAttachment,
                ('Manager',))

setDefaultRoles(ManageConversation,
                ('Manager', 'Reviewer'))

setDefaultRoles(ManageComment,
                ('Manager', 'Reviewer'))

setDefaultRoles(ApproveComment,
                ('Manager', 'Reviewer'))
