#-----------------------------------------------------------------------------
# Name:        __init__.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: __init__.py,v 1.1.1.3 2003/04/02 20:59:45 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------
# CMF based tool for installing/uninstalling CMF products


from Products.CMFCore import utils
import QuickInstallerTool

import sys
this_module = sys.modules[ __name__ ]

tools = ( QuickInstallerTool.QuickInstallerTool,
          )
          
z_tool_bases = utils.initializeBasesPhase1( tools, this_module )
quickinstaller_globals = globals()


def initialize( context ):
    utils.initializeBasesPhase2( z_tool_bases, context )
    utils.ToolInit( 'CMF QuickInstaller Tool',
                    tools = tools,
                    product_name = 'QuickInstallerTool',
                    icon='tool.gif' 
                    ).initialize( context )

    context.registerClass(
        QuickInstallerTool.QuickInstallerTool,
        meta_type="CMFQuickInstallerTool",
        constructors=(QuickInstallerTool.addQuickInstallerTool,),
        icon = 'tool.gif')         #Visibility was added recently, so may be a problem



    
