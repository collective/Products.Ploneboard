"""
Archetypes derived I18NLayer.

$Id: __init__.py,v 1.2 2003/03/26 10:49:14 vladoi Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.utils import getToolByName, ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import *
from Products.Archetypes import listTypes


PROJECTNAME = "I18NLayer"

pt_globals = globals()

import Patches

def initialize(context):
    # register directory views
    registerDirectory('skins', globals())

    # register the policies
    #from Products.I18NLayer.Extensions import CustomizationPolicy
    #CustomizationPolicy.register(context, globals())

    import I18NLayer

    # content initialization
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME,
        )

    ContentInit(
        '%s Content' % PROJECTNAME,
        content_types = content_types,
        permission = AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

