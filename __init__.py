"""
$Id: __init__.py,v 1.4 2004/04/02 08:06:13 tesdal Exp $
"""

from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.Archetypes.ArchetypeTool import getType
from Products.CMFCore.DirectoryView import registerDirectory
from PloneboardTool import PloneboardTool
import os, os.path

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_BOARD_PERMISSION, ADD_FORUM_PERMISSION, ADD_COMMENT_PERMISSION, ADD_CONVERSATION_PERMISSION

# PloneboardWorkflow requires GLOBALS
import PloneboardWorkflow

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    from types import Ploneboard, PloneboardForum, PloneboardConversation, PloneboardComment
    
    ploneboard_content_type, ploneboard_constructor, ploneboard_fti = process_types(
        (getType('Ploneboard', PROJECTNAME), ),
        PROJECTNAME)
    forum_content_type, forum_constructor, forum_fti = process_types(
        (getType('PloneboardForum', PROJECTNAME), ),
        PROJECTNAME)
    conversation_content_type, conversation_constructor, conversation_fti = process_types(
        (getType('PloneboardConversation', PROJECTNAME), ),
        PROJECTNAME)
    comment_content_type, comment_constructor, comment_fti = process_types(
        (getType('PloneboardComment', PROJECTNAME), ),
        PROJECTNAME)

    # If we put this import line to the top of module then
    # utils will magically point to Ploneboard.utils
    from Products.CMFCore import utils
    utils.ToolInit('Ploneboard Tool', 
            tools=(PloneboardTool, ), 
            product_name='Ploneboard',
            icon='tool.gif'
            ).initialize(context)

    #content_types, constructors, ftis = process_types(
    #    listTypes(PROJECTNAME),
    #    PROJECTNAME)

    #utils.ContentInit(
    #    PROJECTNAME + ' Content',
    #    content_types      = content_types,
    #    permission         = ADD_BOARD_PERMISSION,
    #    extra_constructors = constructors,
    #    fti                = ftis,
    #    ).initialize(context)
    utils.ContentInit('Ploneboard Content',
            content_types=ploneboard_content_type,
            permission=ADD_BOARD_PERMISSION,
            extra_constructors=ploneboard_constructor,
            fti=ploneboard_fti
            ).initialize( context )

    # Register manually for each type instead of using utils.ContentInit, 
    # as they need different permissions.

    context.registerClass(PloneboardForum.PloneboardForum,
                          constructors = forum_constructor,
                          permission = ADD_FORUM_PERMISSION)

    context.registerClass(PloneboardConversation.PloneboardConversation,
                          constructors = conversation_constructor,
                          permission = ADD_CONVERSATION_PERMISSION)

    context.registerClass(PloneboardComment.PloneboardComment,
                          constructors = comment_constructor,
                          permission = ADD_COMMENT_PERMISSION)
