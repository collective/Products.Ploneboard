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

$Id: ATDocument.py,v 1.3 2004/03/17 20:46:44 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from schemata import ATDocumentSchema


class ATDocument(BaseContent):
    """An Archetypes derived version of CMFDefault's Document"""

    schema         =  ATDocumentSchema

    content_icon   = 'document_icon.gif'
    meta_type      = 'ATDocument'
    archetype_name = 'AT Document'
    newTypeFor     = 'Document'
    TypeDescription= ''

    __implements__ = BaseContent.__implements__, IATContentType

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/document_view',
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
    
    # backward compat
    text_format = 'text/plain'

    security.declarePublic('CookedBody')
    def CookedBody(self, stx_level='ignored'):
        """Dummy attribute to allow drop-in replacement of Document"""
        return self.getText()

    def setText(self, value, **kwargs):
        """Body text mutator
        
        * set text_format for backward compatibility with std cmf types
        """
        field = self.getField('text')
        field.set(self, value, **kwargs)
        # XXX not nice
        bu = self.getRawText(maybe_baseunit=1)
        if hasattr(bu, 'mimetype'):
            self.text_format = str(bu.mimetype)

registerType(ATDocument, PROJECTNAME)
