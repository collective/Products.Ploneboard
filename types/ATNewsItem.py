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

$Id: ATNewsItem.py,v 1.2 2004/03/20 16:08:53 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATNewsItem import IATNewsItem
from schemata import ATNewsItemSchema


class ATNewsItem(BaseContent):
    """An Archetypes derived version of CMFDefault's Document"""

    schema         =  ATNewsItemSchema

    content_icon   = 'newsitem_icon.gif'
    meta_type      = 'ATNewsItem'
    archetype_name = 'AT News Item'
    newTypeFor     = 'NewsItem'
    TypeDescription= ''
    assocMimetypes = ()
    assocFileExt   = ('news', )

    __implements__ = BaseContent.__implements__, IATNewsItem

    security       = ClassSecurityInfo()
    
    # backward compat
    text_format = 'text/plain'

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/newsitem_view',
       'permissions' : (CMFCorePermissions.View,)
        },
       {
       'id'          : 'edit',
       'name'        : 'Edit',
       'action'      : 'string:${object_url}/atct_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       )

    security.declarePublic('CookedBody')
    def CookedBody(self, stx_level='ignored'):
        """Dummy attribute to allow drop-in replacement of Document"""
        return self.getText()

    def setText(self, value, **kwargs):
        """set text_format for backward compatibility with std cmf types"""
        field = self.getField('text')
        field.set(self, value, **kwargs)
        bu = self.getRawText(maybe_baseunit=1)
        if hasattr(bu, 'mimetype'):
            self.text_format = str(bu.mimetype)

registerType(ATNewsItem, PROJECTNAME)
