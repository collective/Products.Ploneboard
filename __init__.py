# -*- coding: iso-8859-1 -*-

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: __init__.py,v 1.6 2004/12/28 10:50:14 ajung Exp $
"""

from Products.CMFCore.DirectoryView import registerDirectory
from config import SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR, GLOBALS)

# make refresh possible
from SchemaEditor import SchemaEditor
from ParentManagedSchema import ParentManagedSchema

import Products.CMFCore
from Products.Archetypes import process_types
from Products.Archetypes.public import listTypes
from config import *
from Products.CMFCore.CMFCorePermissions import AddPortalContent 

def initialize(context):
    import examples.content
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME),
                                                      PKG_NAME)

    import SchemaEditorTool as SET

    context.registerClass( 
        SET.SchemaEditorTool,
        permission='Add SchemaEditorTool', 
        constructors=(SET.manage_addSchemaEditorToolForm, SET.manage_addSchemaEditorTool),
        icon='www/index.gif'
        )

    Products.CMFCore.utils.ContentInit(
        '%s Example Content' % PKG_NAME,
        content_types      = content_types,
        permission         = AddPortalContent,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

