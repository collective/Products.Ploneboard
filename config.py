# -*- coding: latin-1 -*-
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

$Id: config.py,v 1.25 2004/06/16 20:02:17 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.Permissions import ADD_CONTENT_PERMISSION, ADD_TOPIC_PERMISSION
from Products.CMFCore import CMFCorePermissions
import string

try:
    True
except NameError:
    True  = 1
    False = 0

###############################################################################
## user options
## The options in this section can be overwritten by customconfig

## enable mxTidy for ATDocument and ATNewsItem?
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

## enable external storage
## requires ExternalStorage from Christian Scholz
EXT_STORAGE_ENABLE = False
    
## use TemplateMixin?
## if enabled users can choose between different view templates for each object
ENABLE_TEMPLATE_MIXIN = False

## TemplateMixin write permission. Only if the member has this permission he
## is allowed to choose another permission then the default permission
TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ModifyPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ReviewPortalContent
# TEMPLATE_MIXIN_PERMISSION = CMFCorePermissions.ManagePortal

## use RestrainedMixin?
## if enabled you can restrain allowed types.on a ATCT Folder
ENABLE_RESTRAIN_TYPES_MIXIN = False
RESTRAIN_TYPES_MIXIN_PERMISSION = CMFCorePermissions.ManagePortal
#RESTRAIN_TYPES_MIXIN_PERMISSION = CMFCorePermissions.ModifyPortalContent
#RESTRAIN_TYPES_MIXIN_PERMISSION = CMFCorePermissions.ReviewPortalContent

## Document History view permission
HISTORY_VIEW_PERMISSION = CMFCorePermissions.ModifyPortalContent
# HISTORY_VIEW_PERMISSION = CMFCorePermissions.View

## maximum upload size for ATImage and ATFile in MB. 0 is infinitiv
MAX_FILE_SIZE = 0.0
MAX_IMAGE_SIZE = 0.0

###############################################################################
## private options

PROJECTNAME = "ATContentTypes"
SKINS_DIR = 'skins'

GLOBALS = globals()

CONFIGUREABLE = ('MX_TIDY_ENABLED', 'MX_TIDY_OPTIONS', 'EXT_STORAGE_ENABLE',
                 'ENABLE_TEMPLATE_MIXIN', 'TEMPLATE_MIXIN_PERMISSION',
                 'HISTORY_VIEW_PERMISSION', 'MAX_FILE_SIZE', 'MAX_IMAGE_SIZE',
                 'ENABLE_RESTRAIN_TYPES_MIXIN', 'RESTRAIN_TYPES_MIXIN_PERMISSION',
                 )

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

## ExternalStorage available?
try:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
except ImportError:
    HAS_EXT_STORAGE = False
else:
    HAS_EXT_STORAGE = True

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True

## workflow mapping for the installer
WORKFLOW_DEFAULT  = '(Default)'
WORKFLOW_FOLDER   = 'folder_workflow'
WORKFLOW_TOPIC    = 'folder_workflow'
WORKFLOW_CRITERIA = ''

## icon map used for overwriting ATFile icons
ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}

GOOD_CHARS = string.ascii_letters + string.digits + '._'
CHAR_MAPPING = {
    ' ' : '_',
    'À' : 'A',
    'Á' : 'A',
    'Â' : 'A',
    'Ã' : 'A',
    'Ä' : 'Ae',
    'Å' : 'A',
    'Æ' : 'Ae',
    'Ç' : 'C',
    'È' : 'E',
    'É' : 'E',
    'Ê' : 'E',
    'Ë' : 'E',
    'Ì' : 'I',
    'Í' : 'I',
    'Î' : 'I',
    'Ï' : 'I',
    'Ð' : 'D',
    'Ñ' : 'N',
    'Ò' : 'O',
    'Ó' : 'O',
    'Ô' : 'O',
    'Õ' : 'O',
    'Ö' : 'Oe',
    'Ø' : 'Oe',
    'Ù' : 'U',
    'Ú' : 'U',
    'Û' : 'U',
    'Ü' : 'Ue',
    'Ý' : 'Y',
    'ß' : 'ss',
    'à' : 'a',
    'á' : 'a',
    'â' : 'a',
    'ã' : 'a',
    'ä' : 'ae',
    'å' : 'aa',
    'æ' : 'ae',
    'ç' : 'c',
    'è' : 'e',
    'é' : 'e',
    'ê' : 'e',
    'ë' : 'e',
    'ì' : 'i',
    'í' : 'i',
    'î' : 'i',
    'ï' : 'i',
    'ð' : 'd',
    'ñ' : 'n',
    'ò' : 'o',
    'ó' : 'o',
    'ô' : 'o',
    'õ' : 'o',
    'ö' : 'oe',
    'ø' : 'oe',
    'ù' : 'u',
    'ú' : 'u',
    'û' : 'u',
    'ü' : 'ue',
    'ý' : 'y',
    'ÿ' : 'y',
    }

MIME_ALIAS = {
    'plain' : 'text/plain',
    'stx'   : 'text/structured',
    'html'  : 'text/html',
    'rest'  : 'text/x-rst',
    'structured-text' : 'text/structured',
    'restructuredtext' : 'text/x-rst',
    }
