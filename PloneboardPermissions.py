"""
$Id: PloneboardPermissions.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
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
AddMessage = 'Ploneboard: Add Message'
AddMessageReply = 'Ploneboard: Add Message Reply'
EditMessage = 'Ploneboard: Edit Message'
AddAttachment = 'Ploneboard: Add Message Attachment'
ManageConversation = 'Ploneboard: Manage Conversation'
ManageMessage = 'Ploneboard: Manage Message'
ApproveMessage = 'Ploneboard: Approve Message'

# Set up default roles for permissions
setDefaultRoles(ViewBoard,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(SearchBoard,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(AddBoard,
                ('Manager', 'Owner'))

setDefaultRoles(ManageBoard,
                ('Manager', 'Owner'))

setDefaultRoles(AddMessage,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(AddMessageReply,
                ('Anonymous', 'Member', 'Manager'))

setDefaultRoles(EditMessage,
                ('Manager',))

setDefaultRoles(AddAttachment,
                ('Manager',))

setDefaultRoles(ManageConversation,
                ('Manager', 'Reviewer'))

setDefaultRoles(ManageMessage,
                ('Manager', 'Reviewer'))

setDefaultRoles(ApproveMessage,
                ('Manager', 'Reviewer'))

