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

$Id: ATContentType.py,v 1.5 2004/04/11 19:44:17 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.Archetypes.TemplateMixin import TemplateMixin
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from copy import copy

from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from Products.ATContentTypes.types.schemata import ATContentTypeSchema

def updateActions(klass, actions):
    kactions = copy(klass.actions)
    aids  = [action.get('id') for action in actions ]
    actions = list(actions)
   
    for kaction in kactions:
        kaid = kaction.get('id')
        if kaid not in aids:
            actions.append(kaction)
    
    return tuple(actions)

class ATCTMixin(TemplateMixin):
    """Mixin class for AT Content Types"""
    schema         =  ATContentTypeSchema

    #content_icon   = 'document_icon.gif'
    meta_type      = 'ATContentType'
    archetype_name = 'AT Content Type'
    immediate_view = 'base_view'
    suppl_views    = ()
    newTypeFor     = ''
    typeDescription= ''
    typeDescMsgId  = ''
    assocMimetypes = ()
    assocFileExt   = ()

    __implements__ = IATContentType

    security       = ClassSecurityInfo()   

    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/view',
        'permissions' : (CMFCorePermissions.View,)
         },
        {
        'id'          : 'edit',
        'name'        : 'Edit',
        'action'      : 'string:${object_url}/atct_edit',
        'permissions' : (CMFCorePermissions.ModifyPortalContent,),
         },
        )

    security.declareProtected(CMFCorePermissions.View, 'getLayout')
    def getLayout(self, **kw):
        """Get the current layout or the default layout if the current one is None
        """
        if kw.has_key('schema'):
            schema = kw['schema']
        else:
            schema = self.Schema()
            kw['schema'] = schema
        value =  schema['layout'].get(self, **kw)
        if value:
            return value
        else:
            return self.getDefaultLayout()

    security.declareProtected(CMFCorePermissions.View, 'getDefaultLayout')
    def getDefaultLayout(self):
        """Get the default layout used for TemplateMixin
        """
        return self.immediate_view

InitializeClass(ATCTMixin)

class ATCTContent(ATCTMixin, BaseContent):
    """Base class for non folderish AT Content Types"""

    __implements__ = BaseContent.__implements__, IATContentType
    
    security       = ClassSecurityInfo()
    actions = updateActions(ATCTMixin,
        ({
          'id'          : 'external_edit',
          'name'        : 'External Edit',
          'action'      : 'string:${object_url}/external_edit',
          'permissions' : (CMFCorePermissions.ModifyPortalContent,),
          'visible'     : 0,
         },
        )
    )

InitializeClass(ATCTContent)

class ATCTFolder(ATCTMixin, BaseFolder):
    """Base class for folderish AT Content Types (but not for folders)"""

    __implements__ = BaseFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

InitializeClass(ATCTFolder)

class ATCTOrderedFolder(ATCTMixin, OrderedBaseFolder):
    """Base class for orderable folderish AT Content Types"""

    __implements__ = OrderedBaseFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

InitializeClass(ATCTOrderedFolder)

class ATCTBTreeFolder(ATCTMixin, BaseBTreeFolder):
    """Base class for folderish AT Content Types using a BTree"""

    __implements__ = BaseBTreeFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

InitializeClass(ATCTBTreeFolder)

__all__ = ('ATCTContent', 'ATCTFolder', 'ATCTOrderedFolder', 'ATCTBTreeFolder', 'updateActions' )
