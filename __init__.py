"""
##############################################################################
#
# Copyright (c) 2003 struktur AG and Contributors. # All Rights Reserved.
# # This software is subject to the provisions of the Zope Public License,# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# $Id: __init__.py,v 1.4 2004/09/20 05:49:48 panjunyong Exp $ (Author: $Author: panjunyong $)
"""


from AccessControl import ModuleSecurityInfo
from Globals import InitializeClass
import Products.CMFCore.utils
import catalogawarehook
from Products.CMFCore.DirectoryView import registerDirectory

ADD_CONTENT_PREMISSIONS = 'Manage Portal'
lang_globals = globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/squid_tool', globals())

PKG_NAME = "CMFSquidTool"

from Products.CMFSquidTool.SquidTool import SquidTool
tools = (SquidTool,)

def initialize(context):
    Products.CMFCore.utils.ToolInit("Squid Tool", tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)

types_globals=globals()
