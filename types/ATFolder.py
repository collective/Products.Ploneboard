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

$Id: ATFolder.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import OrderedBaseFolder, BaseFolder, registerType
from Products.CMFCore import CMFCorePermissions
from OFS.ObjectManager import REPLACEABLE
from ComputedAttribute import ComputedAttribute
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from schemata import ATFolderSchema, ATBTreeFolderSchema


class ATFolder(OrderedBaseFolder):
    """A simple folderish archetype"""

    schema         =  ATFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATFolder'
    archetype_name = 'AT Folder'
    immediate_view = 'folder_listing'
    newTypeFor     = 'Plone Folder'
    TypeDescription= ''

    __implements__ = OrderedBaseFolder.__implements__, IATContentType

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'folderContents',
       'name'        : 'Contents',
       'action'      : 'string:${folder_url}/folder_contents',
       'permissions' : (CMFCorePermissions.ListFolderContents,),
       'condition'   : 'python:object.displayContentsTab()'
        },    
       {
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${folder_url}/',
       'permissions' : (CMFCorePermissions.View,)
        },

       {
       'id'          : 'edit',
       'name'        : 'Edit',
       'action'      : 'string:${folder_url}/atct_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       {
       'id'          : 'local_roles',
       'name'        : 'Local Roles',
       'action'      : 'string:${folder_url}/folder_localrole_form',
       'permissions' : (CMFCorePermissions.ManageProperties,),
        },
       )

    def index_html(self):
        """ Acquire if not present. """
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

registerType(ATFolder, PROJECTNAME)

from Products.Archetypes.public import BaseBTreeFolder
    
class ATBTreeFolder(BaseBTreeFolder):
    """A simple btree folderish archetype"""
    schema         =  ATFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATBTreeFolder'
    archetype_name = 'AT BTree Folder'
    immediate_view = 'folder_listing'
    global_allow   = 0
    newTypeFor     = 'Plone Large Folder'
    TypeDescription= ''

    __implements__ = BaseBTreeFolder.__implements__, IATContentType

    security       = ClassSecurityInfo()

registerType(ATBTreeFolder, PROJECTNAME)

