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

$Id: ATFile.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import BaseContent, registerType
from urllib import quote
from Products.ATContentTypes.config import ICONMAP
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from schemata import ATFileSchema


class ATFile(BaseContent):
    """A Archetype derived version of CMFDefault's File"""

    schema         =  ATFileSchema

    content_icon   = 'file_icon.gif'
    meta_type      = 'ATFile'
    archetype_name = 'AT File'
    newTypeFor     = 'File'
    TypeDescription= ''

    __implements__ = BaseContent.__implements__, IATContentType

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/file_view',
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
        return self.file.index_html(REQUEST, RESPONSE)

    security.declarePublic('getIcon')   
    def getIcon(self, relative_to_portal=0):
        try: 
            mimetype_registry=getToolByName(self,'mimetypes_registry',None)
            contenttype = self.getField('file').getContentType(self)
            if ICONMAP.has_key(contenttype):
                icon = quote(ICONMAP[contenttype])
            elif ICONMAP.has_key(contenttype.split('/')[0]):
                icon = quote(ICONMAP[contenttype.split('/')[0]])
            elif (mimetype_registry!=None):                	    	
               	mimetypeitem=mimetype_registry.lookup(contenttype)                                             
               	if (mimetypeitem==None):
               	   return BaseContent.getIcon(self, relative_to_portal)
            	icon=mimetypeitem[0].icon_path                        	            	
            if relative_to_portal:
                return icon
            else:
                # Relative to REQUEST['BASEPATH1']
                portal_url = getToolByName( self, 'portal_url' )
                res = portal_url(relative=1) + '/' + icon
                while res[:1] == '/':
                    res = res[1:]
                return res
        except:
            return BaseContent.getIcon(self, relative_to_portal)

    security.declarePublic('icon')
    icon = getIcon  # For the ZMI     

    security.declareProtected(CMFCorePermissions.View, 'get_data')
    def get_data(self):
        return self.getFile()

    data = ComputedAttribute(get_data, 1)

    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        f = self.getFile()
        return f and f.get_size() or 0
    
    security.declareProtected(CMFCorePermissions.View, 'get_content_type')
    def get_content_type(self):
        f = self.getFile()
        return f and f.getContentType(self) or '' #'application/octet-stream'

    content_type = ComputedAttribute(get_content_type, 1)
 
registerType(ATFile, PROJECTNAME)

