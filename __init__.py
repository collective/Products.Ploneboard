"""
$Id: __init__.py,v 1.1 2003/03/27 09:45:11 magnusheino Exp $
"""
from Products.CMFCore.DirectoryView import registerDirectory
from Globals import package_home
from Products.CMFCore import utils
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
import os, os.path

from config import *

registerDirectory('skins', globals())

def initialize(context):
    ##Import Types here to register them
    import MPoll

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

types_globals=globals()
