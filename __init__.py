from Products.Archetypes import process_types
from Products.Archetypes.debug import log
from Products.Archetypes.ArchetypeTool import  registerType
from Products.Archetypes.public import listTypes
from Products.Archetypes.utils import pathFor
from Products.CMFCore.utils import manage_addContentForm, manage_addContent, \
     manage_addTool, ContentInit
import Products.CMFCore

import os, os.path
import Products.CMFCore.CMFCorePermissions as CMFCorePermissions
from MemberPermissions import ADD_MEMBER_PERMISSION, ADD_MDC_PERMISSION, \
     ContentPermissionMap

import utils
from config import PKG_NAME, SKIN_NAME, GLOBALS, VERSION, TARGET_DIR

Products.CMFCore.DirectoryView.registerDirectory('skins', GLOBALS)

def initialize(context):
    import Member
    import MemberDataContainer
    import RegistrationTool, MembershipTool, MemberCatalogTool, ControlTool, CatalogTool
    
    target_dir = TARGET_DIR
       	    
    # This policy enables an option to install CMFMember at Plone site creation
    import policy
    policy.register(context, GLOBALS)

    my_types = listTypes(PKG_NAME)
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME),
                                                      PKG_NAME)

    type_map = utils.separateTypesByPerm(
        my_types,
        content_types,
        constructors,
        ContentPermissionMap
        )

    i = 0
    for permission in type_map:
        factory_info = type_map[ permission ]
        content_types = tuple([fi[0] for fi in factory_info])
        constructors  = tuple([fi[1] for fi in factory_info])

        ContentInit(
            PKG_NAME + ' Content %d' % i,
            content_types      = content_types,
            permission         = permission,
            extra_constructors = constructors,
            fti                = ftis,
            ).initialize(context)

        i += 1


    tools = (
        RegistrationTool.RegistrationTool,
        MembershipTool.MembershipTool,
        MemberCatalogTool.MemberCatalogTool,
        ControlTool.ControlTool,
        )
    
    icons = {
        RegistrationTool.RegistrationTool:"pencil_icon.gif",
        MembershipTool.MembershipTool:"user.gif",
        #CatalogTool.CatalogTool:"book_icon.gif",
        MemberCatalogTool.MemberCatalogTool:"member_catalog_icon.png",
        ControlTool.ControlTool:"cmfmember_control_icon.png",
        }

    # XXX: TBF
    #for tool in tools:
    #    Products.CMFCore.utils.ToolInit(PKG_NAME + ' Tool', tools=(tool,),
    #                   product_name=PKG_NAME,
    #                   icon=icons[tool],
    #                   ).initialize(context)

    Products.CMFCore.utils.ToolInit(PKG_NAME + ' Tool', tools=tools,
                   product_name=PKG_NAME,
                   icon="cmfmember_control_icon.png",
                   ).initialize(context)

    import migrations
    migrations.registerMigrations()

    import setup
