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


"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.types.ATContentType import translateMimetypeAlias
from Products.ATContentTypes.types.ATDocument import ATDocument
from Products.ATContentTypes.interfaces.IATNewsItem import IATNewsItem
from Products.ATContentTypes.types.schemata import ATNewsItemSchema


class ATNewsItem(ATDocument):
    """A AT news item based on AT Document
    """

    schema         =  ATNewsItemSchema

    content_icon   = 'newsitem_icon.gif'
    meta_type      = 'ATNewsItem'
    archetype_name = 'AT News Item'
    immediate_view = 'newsitem_view'
    default_view   = 'newsitem_view'
    suppl_views    = ()
    newTypeFor     = ('News Item', 'News Item')
    typeDescription= ("A news item is a small piece of news that "
                      "is published \non the front page. "
                      "Add the relevant details below, and press 'Save'.")
    typeDescMsgId  = 'description_edit_news_item'
    assocMimetypes = ()
    assocFileExt   = ('news', )
    cmf_edit_kws   = ATDocument.cmf_edit_kws

    __implements__ = ATDocument.__implements__, IATNewsItem

    security       = ClassSecurityInfo()

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, text, description=None, text_format=None, **kwargs):
        if description is not None:
            self.setDescription(description)
        self.setText(text, mimetype=translateMimetypeAlias(text_format))
        self.update(**kwargs)

registerType(ATNewsItem, PROJECTNAME)
