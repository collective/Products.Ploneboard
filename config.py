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
"""

$Id: config.py,v 1.14 2004/04/02 21:30:25 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Permissions import ADD_CONTENT_PERMISSION, ADD_TOPIC_PERMISSION
from Products.CMFCore import CMFCorePermissions

try:
    True
except NameError:
    True  = 1
    False = 0

###############################################################################
## user options

## enable mxTidy for ATDocument?
MX_TIDY_ENABLED = True

## use TemplateMixin?
## if enabled users can choose between different view templates for each object
ENABLE_TEMPLATE_MIXIN = True

## TemplateMixin write permission. Only if the member has this permission he
## is allowed to choose another permission then the default permission
TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ModifyPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ReviewPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ManagePortal

## Document History view permission
##
HISTORY_VIEW_PERMISSION = CMFCorePermissions.ModifyPortalContent
# HISTORY_VIEW_PERMISSION = CMFCorePermissions.View

###############################################################################
## Don't change anything below here!

PROJECTNAME = "ATContentTypes"
SKINS_DIR = 'skins'

GLOBALS = globals()

## Load the validation package from Products.validation (1) or from the
## python site-packages (0)
## Archetypes 1.2.x requires:  0
## Archetypes 1.2.5+ requires: 1
## Archetypes 1.3.x requires:  1 
VALIDATION_IN_PRODUCTS = True

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

## options for mxTidy
## read http://www.egenix.com/files/python/mxTidy.html for more informations
MX_TIDY_OPTIONS= {
    'drop_font_tags'   : 1,
    'drop_empty_paras' : 1,
    'input_xml'        : 0,
    'output_xhtml'     : 1,
    'quiet'            : 1,
    'show_warnings'    : 1, # -v
    'tab_size'         : 4,
    'wrap'             : 72,
    #'indent'           : 'auto',
    'indent_spaces'    : 1,
    'word_2000'        : 1,
    'char_encoding'    : 'raw',
    }

## workflow mapping for the installer
WORKFLOW_DEFAULT  = '(Default)'
WORKFLOW_FOLDER   = 'folder_workflow'
WORKFLOW_TOPIC    = 'folder_workflow'
WORKFLOW_CRITERIA = ''

## icon map used for overwriting ATFile icons
ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}
