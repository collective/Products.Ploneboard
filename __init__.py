from Globals import package_home
from Products.CMFTypes import process_types
from Products.CMFTypes.debug import log
from Products.CMFTypes import listTypes, registerType
from Products.CMFTypes.utils import pathFor
from Products.CMFCore  import DirectoryView, utils
import os, os.path

PKG_NAME = "CMFMember"
SKIN_NAME = "member"
PERMISSION = "Manage Users"

global GLOBALS
GLOBALS = globals()

DirectoryView.registerDirectory('skins', GLOBALS)


def initialize(context):
    ##Import Types here to register them
    import types
    from MemberDataTool import MemberDataTool
    
    homedir = package_home(GLOBALS)
    target_dir = os.path.join(homedir, 'skins', SKIN_NAME)
    
    content_types, constructors, ftis = process_types(listTypes(),
                                                      PKG_NAME,
                                                      target_dir=target_dir
                                                      )
    utils.ContentInit(
        '%s Content' % PKG_NAME,
        content_types      = content_types,
        permission         = PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    


    tools = (
        MemberDataTool,
        )
        
    utils.ToolInit(PKG_NAME + " Tool", tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)
    
