from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils as CMFCoreUtils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from config import SKINS_DIR, GLOBALS, PROJECT_NAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    import AmazonItem

    content_types, constructors, ftis = process_types(
        listTypes(PROJECT_NAME),
        PROJECT_NAME)

    CMFCoreUtils.ContentInit(
        PROJECT_NAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
