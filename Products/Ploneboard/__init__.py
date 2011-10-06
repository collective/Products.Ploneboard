from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Ploneboard.PloneboardTool import PloneboardTool

import sys

from Products.Ploneboard.config import SKINS_DIR, GLOBALS, PROJECTNAME
import Products.Ploneboard.catalog

registerDirectory(SKINS_DIR, GLOBALS)

this_module = sys.modules[ __name__ ]

def initialize(context):
    ##Import Types here to register them
    import Products.Ploneboard.content

    # If we put this import line to the top of module then
    # utils will magically point to Ploneboard.utils
    from Products.CMFCore import utils
    utils.ToolInit('Ploneboard Tool', 
            tools=(PloneboardTool,), 
            icon='tool.gif'
            ).initialize(context)

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    # Assign an own permission to all content types
    # Heavily based on Bricolite's code from Ben Saller
    import permissions as perms

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            # Add permissions look like perms.Add{meta_type}
            permission         = getattr(perms, 'Add%s' % atype.meta_type),
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

              
    from AccessControl import allow_class      
    from batch import Batch
    allow_class(Batch)
    this_module.Batch = Batch

# Avoid breaking old Ploneboard instances when moving content types modules
# from Ploneboard/types/ to Ploneboard/content/
import content
sys.modules['Products.Ploneboard.types'] = content
