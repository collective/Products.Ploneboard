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

$Id: ATFavorite.py,v 1.3 2004/03/20 16:08:53 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATFavorite import IATFavorite
from ComputedAttribute import ComputedAttribute
from schemata import ATFavoriteSchema

class ATFavorite(BaseContent):
    """An Archetypes derived version of CMFDefault's Favorite"""

    schema         =  ATFavoriteSchema

    content_icon   = 'favorite_icon.gif'
    meta_type      = 'ATFavorite'
    archetype_name = 'AT Favorite'
    include_default_actions = 0
    #global_allow   = 0
    newTypeFor     = 'Favorite'
    TypeDescription= ''
    assocMimetypes = ()
    assocFileExt   = ('fav', )

    __implements__ = BaseContent.__implements__, IATFavorite

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/favorite_view',
       'permissions' : (CMFCorePermissions.View,)
        },
       {
       'id'          : 'edit',
       'name'        : 'Edit',
       'action'      : 'string:${object_url}/atct_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       )

    # Support for preexisting api
    security.declareProtected(CMFCorePermissions.View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """returns the remote URL of the Link
        """
        # need to check why this is different than PortalLink
        portal_url = getToolByName(self, 'portal_url')
        url = self._getRemoteUrl()
        if url:
            if url.startswith('/'):
                url = url[1:]
            return '%s/%s' % (portal_url(), url)
        else:
            return portal_url()
        
    remote_url = ComputedAttribute(getRemoteUrl, 1)
        
    security.declareProtected(CMFCorePermissions.View, 'getIcon')
    def getIcon(self, relative_to_portal=0):
        """Instead of a static icon, like for Link objects, we want
        to display an icon based on what the Favorite links to.
        """
        try:
            return self.getObject().getIcon(relative_to_portal)
        except Exception, msg: # XXX iiigh except all
            return 'favorite_broken_icon.gif'

    security.declareProtected(CMFCorePermissions.View, 'getObject')
    def getObject(self):
        """Return the actual object that the Favorite is
        linking to
        """
        portal_url = getToolByName(self, 'portal_url')
        return portal_url.getPortalObject().restrictedTraverse(self._getRemoteUrl())

registerType(ATFavorite, PROJECTNAME)
