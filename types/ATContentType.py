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

$Id: ATContentType.py,v 1.12 2004/06/09 13:59:19 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

from copy import copy

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import BaseContent, BaseFolder
    from Products.LinguaPlone.public import OrderedBaseFolder,BaseBTreeFolder
else:
    from Products.Archetypes.public import BaseContent, BaseFolder
    from Products.Archetypes.public import OrderedBaseFolder,BaseBTreeFolder

from Products.Archetypes.TemplateMixin import TemplateMixin

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass

from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from Products.ATContentTypes.types.schemata import ATContentTypeSchema


def updateActions(klass, actions):
    """Merge the actions from a class with a list of actions
    """
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
    default_view   = 'base_view'
    suppl_views    = ()
    newTypeFor     = ()
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
        return self.default_view
    
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'edit')
    def edit(self, *args, **kwargs):
        """Reimplementing edit() to have a compatibility method for the old
        cmf edit() method
        """
        if len(args) != 0:
            # use cmf edit method
            return self.cmf_edit(*args, **kwargs)
        
        fieldNames = [field.getName() for field in self.Schema().fields()]
        for name in kwargs.keys():
            if name not in fieldNames:
                # we are trying to
                return self.cmf_edit(**kwargs)
        # standard AT edit - redirect to update()
        return self.update(self, **kwargs)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, *args, **kwargs):
        """Overwrite this method to make AT compatible with the crappy CMF edit()
        """
        raise NotImplementedError("cmf_edit method isn't implemented")

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
        {
        'id'          : 'local_roles',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,),
         },
        )
    )

InitializeClass(ATCTContent)

class ATCTFileContent(ATCTContent):
    """Base class for content types containing a file like ATFile or ATImage
    
    The file field *must* be only primary field
    """

    security       = ClassSecurityInfo()
    actions = updateActions(ATCTContent,
        ({
        'id'          : 'download',
        'name'        : 'Download',
        'action'      : 'string:${object_url}',
        'permissions' : (CMFCorePermissions.ModifyPortalContent,)
         },
        )
    )

    security.declareProtected(CMFCorePermissions.View, 'download')
    def download(self, REQUEST, RESPONSE):
        """Download the file (use default index_html)
        """
        return self.index_html(REQUEST, RESPONSE)

    security.declareProtected(CMFCorePermissions.View, 'get_data')
    def get_data(self):
        """CMF compatibility method
        """
        return self.getPrimaryField().get(self)

    data = ComputedAttribute(get_data, 1)

    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        """CMF compatibility method
        """
        f = self.getPrimaryField().get(self)
        return f and f.get_size() or 0

    security.declareProtected(CMFCorePermissions.View, 'size')
    def size(self):
        """Get size (image_view.pt)
        """
        return self.get_size()

    security.declareProtected(CMFCorePermissions.View, 'get_content_type')
    def get_content_type(self):
        """CMF compatibility method
        """
        f = self.getPrimaryField().get(self)
        return f and f.getContentType() or 'text/plain' #'application/octet-stream'

    content_type = ComputedAttribute(get_content_type, 1)

InitializeClass(ATCTFileContent)

class ATCTFolder(ATCTMixin, BaseFolder):
    """Base class for folderish AT Content Types (but not for folders)"""

    __implements__ = BaseFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

    actions = updateActions(ATCTMixin,
        ({
        'id'          : 'local_roles',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,),
         },
        {
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${folder_url}/',
        'permissions' : (CMFCorePermissions.View,),
         },
        )
    )

InitializeClass(ATCTFolder)


class ATCTOrderedFolder(ATCTMixin, OrderedBaseFolder):
    """Base class for orderable folderish AT Content Types"""

    __implements__ = OrderedBaseFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

    actions = updateActions(ATCTMixin,
        ({
        'id'          : 'local_roles',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,),
         },
        {
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${folder_url}/',
        'permissions' : (CMFCorePermissions.View,),
         },
        )
    )

InitializeClass(ATCTOrderedFolder)


class ATCTBTreeFolder(ATCTMixin, BaseBTreeFolder):
    """Base class for folderish AT Content Types using a BTree"""

    __implements__ = BaseBTreeFolder.__implements__, IATContentType
    
    security       = ClassSecurityInfo()

    actions = updateActions(ATCTMixin,
        ({
        'id'          : 'local_roles',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,),
         },
        {
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${folder_url}/',
        'permissions' : (CMFCorePermissions.View,),
         },
        )
    )

InitializeClass(ATCTBTreeFolder)


__all__ = ('ATCTContent', 'ATCTFolder', 'ATCTOrderedFolder', 'ATCTBTreeFolder',
           'updateActions' )
