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

$Id: ATImage.py,v 1.25 2004/07/21 15:22:46 tiran Exp $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute

from Products.ATContentTypes.types.ATContentType import ATCTFileContent, \
    cleanupFilename
from Products.ATContentTypes.interfaces.IATImage import IATImage
from Products.ATContentTypes.types.schemata import ATImageSchema, ATExtImageSchema

from OFS.Image import Image


class ATImage(ATCTFileContent):
    """An Archetypes derived version of CMFDefault's Image"""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    archetype_name = 'AT Image'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    suppl_views    = ()
    newTypeFor     = ('Image', 'Portal Image')
    typeDescription= ("Using this form, you can enter details about the image, \n"
                      "and upload an image if required.")
    typeDescMsgId  = 'description_edit_image'
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )

    __implements__ = ATCTFileContent.__implements__, IATImage

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setImage')
    def setImage(self, value, **kwargs):
        """Set id to uploaded id
        """
        self._setATCTFileContent(value, **kwargs)

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, *args, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.image.tag(*args, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return tag()
    
    security.declareProtected(CMFCorePermissions.View, 'getSize')
    def getSize(self, scale=None):
        field = self.getField('image')
        return field.getSize(self, scale)
    
    security.declareProtected(CMFCorePermissions.View, 'getWidth')
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(CMFCorePermissions.View, 'getHeight')
    def getHeight(self, scale=None):
        return self.getSize(scale)[1]
    
    width = ComputedAttribute(getWidth)
    height = ComputedAttribute(getHeight)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None):
        if file is not None:
            self.setImage(file)
        if title is not None:
            self.setTitle(title)
        self.reindexObject()

registerType(ATImage, PROJECTNAME)


class ATExtImage(ATImage):
    """An Archetypes derived version of CMFDefault's Image with
    external storage
    """

    schema         =  ATExtImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATExtImage'
    archetype_name = 'AT Ext Image'
    newTypeFor     = ''
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'getImage')
    def getImage(self, **kwargs):
        """Return the image with proper content type
        """
        field  = self.getField('image')
        image  = field.get(self, **kwargs)
        ct     = self.getContentType()
        parent = aq_parent(self)
        i      = Image(self.getId(), self.Title(), image, ct)
        return i.__of__(parent)

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """Make it directly viewable when entering the objects URL
        """
        image = self.getImage(REQUEST=REQUEST, RESPONSE=RESPONSE)
        return image.index_html(REQUEST, RESPONSE)

if HAS_EXT_STORAGE:
    registerType(ATExtImage, PROJECTNAME)
