"""
$Id: __init__.py,v 1.1 2003/10/24 13:03:05 tesdal Exp $
"""

import Ploneboard, Forum, Conversation, Message, PloneboardPermissions
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import ToolInit, ContentInit
from Products.CMFCore.DirectoryView import registerDirectory

from PloneboardTool import PloneboardTool

ploneboard_globals=globals()

# PloneboardWorkflow requires ploneboard_globals
import PloneboardWorkflow

# Make the skins available as DirectoryViews.
registerDirectory('skins', ploneboard_globals)

def initialize( context ):
    
    ToolInit('Ploneboard Tool', 
            tools=(PloneboardTool, ), 
            product_name='Ploneboard',
            icon='tool.gif'
            ).initialize(context)

    ContentInit( 'Ploneboard Content'
               , content_types=(Ploneboard.Ploneboard,)
               , permission=PloneboardPermissions.AddBoard
               , extra_constructors=(Ploneboard.addPloneboard,)
               , fti=Ploneboard.factory_type_information
               ).initialize( context )

    # Register manually for each type instead of using utils.ContentInit, 
    # as they need different permissions.

    context.registerClass(Forum.Forum,
                          constructors = (Forum.addForum,),
                          permission = PloneboardPermissions.AddBoard)

    context.registerClass(Conversation.Conversation,
                          constructors = (Conversation.addConversation,),
                          permission = PloneboardPermissions.AddMessage)

    context.registerClass(Message.Message,
                          constructors = (Message.addMessage,),
                          permission = PloneboardPermissions.AddMessage)

