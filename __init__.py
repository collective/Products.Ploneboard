from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.CompositePack.config import *
from Products.CompositePack import design
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins', GLOBALS)

from Products.CompositePage import tool
tool.registerUI('plone', design.PloneUI())
# Avoid shadowing name below
del tool

def initialize(context):

    from Products.CompositePack import tool, viewlet
    from Products.CompositePack.composite import archetype
    from Products.CompositePack.viewlet import container

    # register archetypes content with the machinery
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)

    tools = (tool.CompositeTool,)

    cmf_utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis).initialize(context)

    registerClasses(context, PROJECTNAME, ['CompositePack Element',
                                           'CompositePack Viewlet',
                                           'CompositePack Viewlet Container'])

    context.registerClass(
        tool.CompositeTool,
        constructors=(tool.manage_addCompositeTool,),
        icon='tool.gif',
        )
