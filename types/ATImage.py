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

$Id: ATImage.py,v 1.2 2004/03/20 16:08:53 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.public import BaseSchema, Schema, MetadataSchema
from Products.Archetypes.public import TextField, ImageField
from Products.Archetypes.public import TextAreaWidget, ImageWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore.utils import getToolByName
from urllib import quote
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATImage import IATImage
from schemata import ATImageSchema


class ATImage(BaseContent):
    """An Archetypes derived version of CMFDefault's Image"""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    archetype_name = 'AT Image'
    newTypeFor     = 'Image'
    TypeDescription= ''
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )

    __implements__ = BaseContent.__implements__, IATImage

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/image_view',
       'permissions' : (CMFCorePermissions.View,)
        },
       {
       'id'          : 'edit',
       'name'        : 'Edit',
       'action'      : 'string:${object_url}/atct_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       {
       'id'          : 'external_edit',
       'name'        : 'External Edit',
       'action'      : 'string:${object_url}/external_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       )

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        Display the image, with or without standard_html_[header|footer],
        as appropriate.
        """
        return self.image.index_html(REQUEST, RESPONSE)

    security.declareProtected(CMFCorePermissions.View, 'get_data')
    def get_data(self):
        return self.getImage()

    data = ComputedAttribute(get_data, 1)
    
    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        img = self.getImage()
        return img and img.get_size() or 0
        
    size = ComputedAttribute(get_size, 1)

    security.declareProtected(CMFCorePermissions.View, 'get_content_type')
    def get_content_type(self):
        img = self.getImage()
        return img and img.getContentType(self) or '' #'image/jpeg'

    content_type = ComputedAttribute(get_content_type, 1)

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, *args, **kwargs):
        return self.getImage().tag(*args, **kwargs)

registerType(ATImage, PROJECTNAME)
