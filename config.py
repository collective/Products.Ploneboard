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

$Id: config.py,v 1.7 2004/03/17 20:46:43 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Permissions import ADD_CONTENT_PERMISSION, ADD_TOPIC_PERMISSION

PROJECTNAME = "ATContentTypes"
SKINS_DIR = 'skins'

GLOBALS = globals()

# Load the validation package from Products.validation (1) or from the
# python site-packages (0)
# Archetypes 1.2.x requires:  0
# Archetypes 1.2.5+ requires: 1
# Archetypes 1.3.x requires:  1 
VALIDATION_IN_PRODUCTS = 1

# using special plone 2 stuff?
try:
    from Products.CMFPlone.PloneFolder import ReplaceableWrapper
except ImportError:
    HAS_PLONE2=0
else:
    HAS_PLONE2=1

# mxTidy available?
try:
    import mx.Tidy
except ImportError:
    HAS_MX_TIDY=0
else:
    HAS_MX_TIDY=1

MX_TIDY_MIMETYPES = (
    'text/html',
     )

MX_TIDY_OPTIONS= {
    'drop_font_tags' : 1,
    'input_xml' : 0,
    'output_xhtml' : 1,
    'quiet' : 1,
    'show_warnings' : 1, # -v
    'tab_size' : 4,
    }

# Add attributes to be more CMF compatible?
# XXX more docs here
CMF_COMPATIBILITY_ATTRIBUTS=1

# workflow mapping
WORKFLOW_DEFAULT  = '(Default)'
WORKFLOW_FOLDER   = 'folder_workflow'
WORKFLOW_TOPIC    = 'folder_workflow'
WORKFLOW_CRITERIA = ''

ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}
