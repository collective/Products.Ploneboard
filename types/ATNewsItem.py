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

$Id: ATNewsItem.py,v 1.7 2004/05/14 12:36:04 godchap Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    pass
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.types.ATDocument import ATDocument
from Products.ATContentTypes.interfaces.IATNewsItem import IATNewsItem
from Products.ATContentTypes.types.schemata import ATNewsItemSchema


class ATNewsItem(ATDocument):
    """A AT news item based on AT Document
    """

    schema         =  ATNewsItemSchema

    content_icon   = 'newsitem_icon.gif'
    meta_type      = 'ATNewsItem'
    archetype_name = 'AT News Item'
    immediate_view = 'newsitem_view'
    default_view   = 'newsitem_view'
    suppl_views    = ()
    newTypeFor     = ('News Item', 'News Item')
    typeDescription= "A news item is a small piece of news that is published on the front\n" \
                     "page. Add the relevant details below, and press 'Save'."
    typeDescMsgId  = 'description_edit_news_item'
    assocMimetypes = ()
    assocFileExt   = ('news', )

    __implements__ = ATDocument.__implements__, IATNewsItem

    security       = ClassSecurityInfo()
    
registerType(ATNewsItem, PROJECTNAME)
