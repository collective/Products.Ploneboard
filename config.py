#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
#
"""AT Content Types configuration file

DO NOT CHANGE THIS FILE!

All changes will be overwritten by the next release. Use a customconfig instead.
See customconfig.py.example

$Id: config.py,v 1.16 2004/04/12 01:38:54 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.Permissions import ADD_CONTENT_PERMISSION, ADD_TOPIC_PERMISSION
from Products.CMFCore import CMFCorePermissions

try:
    True
except NameError:
    True  = 1
    False = 0

###############################################################################
## user options
## The options in this section can be overwritten by customconfig

## enable mxTidy for ATDocument?
MX_TIDY_ENABLED = True

## options for mxTidy
## read http://www.egenix.com/files/python/mxTidy.html for more informations
MX_TIDY_OPTIONS= {
    'drop_font_tags'   : 1,
    'drop_empty_paras' : 1,
    'input_xml'        : 0,
    'output_xhtml'     : 1,
    'quiet'            : 1,
    'show_warnings'    : 1,
    'tab_size'         : 4,
    'wrap'             : 72,
    #'indent'           : 'auto',
    'indent_spaces'    : 1,
    'word_2000'        : 1,
    'char_encoding'    : 'raw',
    }

## use TemplateMixin?
## if enabled users can choose between different view templates for each object
ENABLE_TEMPLATE_MIXIN = False

## TemplateMixin write permission. Only if the member has this permission he
## is allowed to choose another permission then the default permission
TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ModifyPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ReviewPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ManagePortal

## Document History view permission
HISTORY_VIEW_PERMISSION = CMFCorePermissions.ModifyPortalContent
# HISTORY_VIEW_PERMISSION = CMFCorePermissions.View

###############################################################################
## private options

PROJECTNAME = "ATContentTypes"
SKINS_DIR = 'skins'

GLOBALS = globals()

CONFIGUREABLE = ('MX_TIDY_ENABLED', 'MX_TIDY_OPTIONS', 'ENABLE_TEMPLATE_MIXIN',
                 'TEMPLATE_MIXIN_PERMISSION', 'HISTORY_VIEW_PERMISSION', )

## using special plone 2 stuff?
try:
    from Products.CMFPlone.PloneFolder import ReplaceableWrapper
except ImportError:
    HAS_PLONE2 = False
else:
    HAS_PLONE2 = True

## mxTidy available?
try:
    import mx.Tidy
except ImportError:
    HAS_MX_TIDY = False
else:
    HAS_MX_TIDY = True

## tidy only these document types
MX_TIDY_MIMETYPES = (
    'text/html',
     )

## workflow mapping for the installer
WORKFLOW_DEFAULT  = '(Default)'
WORKFLOW_FOLDER   = 'folder_workflow'
WORKFLOW_TOPIC    = 'folder_workflow'
WORKFLOW_CRITERIA = ''

## icon map used for overwriting ATFile icons
ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}
