from Products.CMFCore import CMFCorePermissions

# Add a new member
ADD_PERMISSION = CMFCorePermissions.AddPortalMember
# Register a new member, i.e. create a User object and enable a member to log in
REGISTER_PERMISSION = 'CMFMember: Register member'
# Disable a membership
DISABLE_PERMISSION = 'Manage users'
# Modify the member's ID -- should only happen during preregistration
EDIT_ID_PERMISSION = 'CMFMember: Set member id'
# Change a member's password
EDIT_PASSWORD_PERMISSION = CMFCorePermissions.SetOwnPassword
# Change a member's roles and domains
EDIT_SECURITY_PERMISSION = 'Manage users'
# Change a member's registration information
EDIT_REGISTRATION_PERMISSION = 'CMFMember: Edit registration information'
# Change a member's other information
EDIT_OTHER_PERMISSION = CMFCorePermissions.SetOwnProperties
# View a member's roles and domains
VIEW_SECURITY_PERMISSION = 'Manage users'
# View a member's public information
VIEW_PUBLIC_PERMISSION = 'CMFMember: View'
# View a member's private information
VIEW_OTHER_PERMISSION = EDIT_OTHER_PERMISSION
# Appear in searches
VIEW_PERMISSION = CMFCorePermissions.View
# Enable password mailing
MAIL_PASSWORD_PERMISSION = CMFCorePermissions.MailForgottenPassword


