from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.CompositePack.config import *
from Products.CompositePack import design
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CompositePage import tool as base_tool

registerDirectory('skins', GLOBALS)
base_tool.registerUI('plone', design.PloneUI())

def initialize(context):

    from Products.CompositePack import tool, viewlet
    from Products.CompositePack.composite import archetype
    from Products.CompositePack.viewlet import container
    from Products.CompositePack.composite import cmfcompositepage
    from Products.CompositePack.composite import titles
    
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
                                           'CompositePack Titles',
                                           'CompositePack Viewlet Container'])

    context.registerClass(
        tool.CompositeTool,
        meta_type=TOOL_NAME,
        constructors=(tool.manage_addCompositeTool,),
        icon = TOOL_ICON)
             
    cmf_utils.ToolInit(TOOL_NAME,
                       tools = tools,
                       product_name = PROJECTNAME,
                       icon=TOOL_ICON
                   ).initialize(context)
