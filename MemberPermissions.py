from Products.CMFCore import CMFCorePermissions
from utils import ContentPermMap

# Add a new member
ADD_PERMISSION = ADD_MEMBER_PERMISSION = CMFCorePermissions.AddPortalMember
# Add a MemberDataContainer
ADD_MDC_PERMISSION = 'Manage users'
# Register a new member, i.e. create a User object and enable a member to log in
REGISTER_PERMISSION = 'CMFMember: Register member'
# Disable a membership
DISABLE_PERMISSION = 'Manage users'
# Modify the member's ID -- should only happen during preregistration
EDIT_ID_PERMISSION = 'CMFMember: Edit member id'
# Modify the member's general properties
EDIT_PROPERTIES_PERMISSION = CMFCorePermissions.SetOwnProperties
# Change a member's password
EDIT_PASSWORD_PERMISSION = CMFCorePermissions.SetOwnPassword
# Change a member's roles and domains
EDIT_SECURITY_PERMISSION = 'Manage users'
# Appear in searches
VIEW_PERMISSION = CMFCorePermissions.View
# View a member's roles and domains
VIEW_SECURITY_PERMISSION = 'Manage users'
# View a member's public information
VIEW_PUBLIC_PERMISSION = VIEW_PERMISSION
# View a member's private information
VIEW_OTHER_PERMISSION = EDIT_PROPERTIES_PERMISSION
# Enable password mailing
MAIL_PASSWORD_PERMISSION = CMFCorePermissions.MailForgottenPassword

# map types to permissions
ContentPermissionMap = ContentPermMap()
ContentPermissionMap[ ADD_MEMBER_PERMISSION ] = 'Member'
ContentPermissionMap[ ADD_MDC_PERMISSION ] = 'MemberDataContainer'
ContentPermissionMap[ ADD_MDC_PERMISSION ] = 'ControlTool'
# our way of saying all the other content types should get this permission
ContentPermissionMap[ CMFCorePermissions.AddPortalContent ] =  None
