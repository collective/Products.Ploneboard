from Globals import package_home
from Products.Archetypes import process_types
from Products.Archetypes.debug import log
from Products.Archetypes import listTypes, registerType
from Products.Archetypes.utils import pathFor
from Products.CMFCore  import DirectoryView, utils
import os, os.path
import Products.CMFCore.CMFCorePermissions as CMFCorePermissions

PKG_NAME = "CMFMember"
SKIN_NAME = "member"
TYPE_NAME = "Member"  # Name of types_tool type used to hold member data


# Add a new member
ADD_PERMISSION = CMFCorePermissions.AddPortalMember
# Register a new member, i.e. create a User object and enable a member to log in
REGISTER_PERMISSION = 'CMFMember: Register member'
# Modify the member's ID -- should only happen during preregistration
EDIT_ID_PERMISSION = 'CMFMember: Set member id'
# Change a member's password
EDIT_PASSWORD_PERMISSION = CMFCorePermissions.SetOwnPassword
# Change a member's roles and domains
EDIT_SECURITY_PERMISSION = 'Manage users'
# Change a member's registration information
EDIT_REGISTRATION_PERMISSION = CMFCorePermissions.SetOwnProperties
# Change a member's other information
EDIT_OTHER_PERMISSION = CMFCorePermissions.SetOwnProperties
# View a member's roles and domains
VIEW_SECURITY_PERMISSION = 'Manage users'
# View a member's public information
VIEW_PUBLIC_PERMISSION = 'CMFMember: View'
# View a member's private information
VIEW_OTHER_PERMISSION = EDIT_INFO_PERMISSION
# Appear in searches
VIEW_PERMISSION = CMFCorePermissions.View
# Enable password mailing
MAIL_PASSWORD_PERMISSION = CMFCorePermissions.MailForgottenPassword

global GLOBALS
GLOBALS = globals()

DirectoryView.registerDirectory('skins', GLOBALS)


def initialize(context):
    import sys
    ##Import Types here to register them
    import types
    
    homedir = package_home(GLOBALS)
    target_dir = os.path.join(homedir, 'skins', SKIN_NAME)
    
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME),
                                                      PKG_NAME)
    utils.ContentInit(
        '%s Content' % PKG_NAME,
        content_types      = content_types,
        permission         = ADD_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    
    import MemberDataTool
    tools = (
        MemberDataTool.MemberDataTool,
        )

    utils.ToolInit(PKG_NAME + ' Tool', tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)
    