from Globals import package_home
from Products.Archetypes import process_types
from Products.Archetypes.debug import log
from Products.Archetypes.ArchetypeTool import  registerType
from Products.Archetypes.public import listTypes
from Products.Archetypes.utils import pathFor
from Products.CMFCore.utils import manage_addContentForm, manage_addContent, manage_addTool
import Products.CMFCore

import os, os.path
import Products.CMFCore.CMFCorePermissions as CMFCorePermissions
from MemberPermissions import ADD_PERMISSION

PKG_NAME = "CMFMember"
SKIN_NAME = "member"

GLOBALS = globals()

def getVersion():
    src_path = package_home(GLOBALS)
    f =  file(os.path.join(src_path, 'version.txt'))
    return f.read()


VERSION = getVersion()

Products.CMFCore.DirectoryView.registerDirectory('skins', GLOBALS)


def initialize(context):
    ##Import Types here to register them
    import Member
    import MemberDataContainer
    import ControlTool
    
    homedir = package_home(GLOBALS)
    target_dir = os.path.join(homedir, 'skins', SKIN_NAME)
    
    # This policy enables an option to install CMFMember at Plone site creation
    import PloneWithCMFMemberSitePolicy
    PloneWithCMFMemberSitePolicy.register(context, GLOBALS)
    
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME),
                                                      PKG_NAME)

    Products.CMFCore.utils.ContentInit(
        '%s Content' % PKG_NAME,
        content_types      = content_types,
        permission         = ADD_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    
    import RegistrationTool, MembershipTool, CatalogTool, MemberCatalogTool
    tools = (
        RegistrationTool.RegistrationTool,
        MembershipTool.MembershipTool,
        CatalogTool.CatalogTool,
        ControlTool.ControlTool,
        MemberCatalogTool.MemberCatalogTool
        )

    Products.CMFCore.utils.ToolInit(PKG_NAME + ' Tool', tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)

    import migrations
    migrations.registerMigrations()

    import setup
