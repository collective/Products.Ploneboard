#-----------------------------------------------------------------------------
# Name:        __init__.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: __init__.py,v 1.1 2003/04/03 01:09:36 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------
# CMF based tool for tracking active users

from Products.CMFCore.DirectoryView import registerDirectory

from Products.CMFCore import utils
import UserTrackTool

import sys
this_module = sys.modules[ __name__ ]

tools = ( UserTrackTool.UserTrackTool,
          )
          
z_tool_bases = utils.initializeBasesPhase1( tools, this_module )
usertrack_globals = globals()

registerDirectory( 'skins', globals() )
registerDirectory( 'skins/usertrack', globals() )

def initialize( context ):
    utils.initializeBasesPhase2( z_tool_bases, context )
    utils.ToolInit( 'CMF UserTrack Tool',
                    tools = tools,
                    product_name = 'CMFUserTrackTool',
                    icon='tool.gif' #'www/usertrack.gif'
                    ).initialize( context )



    
