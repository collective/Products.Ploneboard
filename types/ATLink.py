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

$Id: ATLink.py,v 1.7 2004/05/14 12:36:04 godchap Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    pass
from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.interfaces.IATLink import IATLink
from Products.ATContentTypes.types.schemata import ATLinkSchema


class ATLink(ATCTContent):
    """An Archetypes derived version of CMFDefault's Link"""

    schema         =  ATLinkSchema

    content_icon   = 'link_icon.gif'
    meta_type      = 'ATLink'
    archetype_name = 'AT Link'
    immediate_view = 'link_view'
    default_view   = 'link_view'
    suppl_views    = ()
    newTypeFor     = ('Link', 'Link')
    typeDescription= "A link is a pointer to a location on the internet or intranet.\n" \
                     "Enter the relevant details below, and press 'Save'."
    typeDescMsgId  = 'description_edit_link_item'
    assocMimetypes = ()
    assocFileExt   = ('link', 'url', )

    __implements__ = ATCTContent.__implements__, IATLink

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'remote_url')
    def remote_url(self):
        """CMF compatibility method
        """
        return self.getRemoteUrl()

registerType(ATLink, PROJECTNAME)
