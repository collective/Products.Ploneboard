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

$Id: ATFolder.py,v 1.15 2004/06/20 15:13:21 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.types.ATContentType import ATCTOrderedFolder, \
    ATCTBTreeFolder
from Products.ATContentTypes.interfaces.IATFolder import IATFolder, \
    IATBTreeFolder
from Products.ATContentTypes.types.schemata import ATFolderSchema,\
    ATBTreeFolderSchema

class ATFolder(ATCTOrderedFolder):
    """A simple folderish archetype"""

    schema         =  ATFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATFolder'
    archetype_name = 'AT Folder'
    immediate_view = 'folder_listing'
    default_view   = 'folder_listing'
    suppl_views    = ()
    newTypeFor     = ('Folder', 'Plone Folder')
    typeDescription= ''
    typeDescMsgId  = ''
    assocMimetypes = ()
    assocFileExt   = ()

    __implements__ = ATCTOrderedFolder.__implements__, IATFolder

    security       = ClassSecurityInfo()

##    actions = updateActions(ATCTOrderedFolder,
##        ({
##         'id'          : 'folderContents',
##         'name'        : 'Contents',
##         'action'      : 'string:${folder_url}/folder_contents',
##         'permissions' : (CMFCorePermissions.ListFolderContents,),
##         'condition'   : 'python:object.displayContentsTab()'
##          },    
##        )
##    )

registerType(ATFolder, PROJECTNAME)

from Products.Archetypes.public import BaseBTreeFolder
    
class ATBTreeFolder(ATCTBTreeFolder):
    """A simple btree folderish archetype"""
    schema         =  ATBTreeFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATBTreeFolder'
    archetype_name = 'AT BTree Folder'
    immediate_view = 'folder_listing'
    default_view   = 'folder_listing'
    suppl_views    = ()
    global_allow   = 0
    newTypeFor     = ('Large Plone Folder', 'Large Plone Folder')
    TypeDescription= ''
    assocMimetypes = ()
    assocFileExt   = ()

    __implements__ = ATCTBTreeFolder.__implements__, IATBTreeFolder

    security       = ClassSecurityInfo()

registerType(ATBTreeFolder, PROJECTNAME)

