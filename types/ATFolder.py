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

$Id: ATFolder.py,v 1.13 2004/05/15 01:53:07 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from OFS.ObjectManager import REPLACEABLE
from ComputedAttribute import ComputedAttribute

from Products.ATContentTypes.types.ATContentType import ATCTOrderedFolder, ATCTBTreeFolder, updateActions
from Products.ATContentTypes.interfaces.IATFolder import IATFolder, IATBTreeFolder
from Products.ATContentTypes.types.schemata import ATFolderSchema, ATBTreeFolderSchema


class ATFolderBase(ATCTOrderedFolder):
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


if HAS_PLONE2:
    # ********** plone 2 **********
    from Products.CMFPlone.PloneFolder import ReplaceableWrapper

    class ATFolder(ATFolderBase):

        #
        # from CMFPlone.PloneFolder
        #

        def index_html(self):
            """ Acquire if not present. """
            _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
            return ReplaceableWrapper(aq_base(_target).__of__(self))
    
        index_html = ComputedAttribute(index_html, 1)
    
        def __browser_default__(self, request):
            """ Set default so we can return whatever we want instead
            of index_html """
            return getToolByName(self, 'plone_utils').browserDefault(self)        
        
        #
        # end of part from CMFPlone
        #

    # ********** plone 2 **********
else:
    # **********   cmf   **********
    class ATFolder(ATFolderBase):
        pass
    
    # **********   cmf   **********

ATFolder.__doc__ = ATFolderBase.__doc__    

registerType(ATFolder, PROJECTNAME)

from Products.Archetypes.public import BaseBTreeFolder
    
class ATBTreeFolder(ATCTBTreeFolder):
    """A simple btree folderish archetype"""
    schema         =  ATFolderSchema

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

