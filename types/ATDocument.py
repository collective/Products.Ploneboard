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

$Id: ATDocument.py,v 1.35 2005/01/24 18:27:05 tiran Exp $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

from types import TupleType

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from ZPublisher.HTTPRequest import HTTPRequest
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute

from Products.ATContentTypes.types.ATContentType import ATCTContent
from Products.ATContentTypes.types.ATContentType import updateActions
from Products.ATContentTypes.types.ATContentType import translateMimetypeAlias
from Products.ATContentTypes.HistoryAware import HistoryAwareMixin
from Products.ATContentTypes.interfaces.IATDocument import IATDocument
from Products.ATContentTypes.types.schemata import ATDocumentSchema

class ATDocument(ATCTContent, HistoryAwareMixin):
    """An Archetypes derived version of CMFDefault's Document"""

    schema         =  ATDocumentSchema

    content_icon   = 'document_icon.gif'
    meta_type      = 'ATDocument'
    archetype_name = 'AT Document'
    default_view   = 'document_view'
    immediate_view = 'document_view'
    suppl_views    = ()
    newTypeFor     = ('Document', 'Document')
    typeDescription= 'Fill in the details of this document.'
    typeDescMsgId  = 'description_edit_document'
    assocMimetypes = ('application/pdf', 'application/xhtml+xml',
                      'application/msword', 'message/rfc822', 'text/*',
                     )
    assocFileExt   = ('doc', 'txt', 'stx', 'rst', 'rest', 'pdf', 'py' )
    cmf_edit_kws   = ('text_format',)

    __implements__ = (ATCTContent.__implements__,
                      IATDocument,
                      HistoryAwareMixin.__implements__,
                     )

    security       = ClassSecurityInfo()

    actions = updateActions(ATCTContent,
                            HistoryAwareMixin.actions
                           )

    # backward compat
    text_format = 'text/plain'

    security.declareProtected(CMFCorePermissions.View, 'CookedBody')
    def CookedBody(self, stx_level='ignored'):
        """CMF compatibility method
        """
        return self.getText()

    # XXX plone news template requires the View permission but
    # would be better ModifyPortalContent
    security.declareProtected(CMFCorePermissions.View, 'EditableBody')
    def EditableBody(self):
        """CMF compatibility method
        """
        return self.getRawText()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'setFormat')
    def setFormat(self, value):
        """CMF compatibility method
        
        The default mutator is overwritten to:
        
          o add a conversion from stupid CMF content type (e.g. structured-text)
            to real mime types used by MTR.
        
          o Set format to default format if value is empty

        """
        if not value:
            value = ATDOCUMENT_CONTENT_TYPE
        else:
            value = translateMimetypeAlias(value)
        ATCTContent.setFormat(self, value)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setText')
    def setText(self, value, **kwargs):
        """Body text mutator

        * hook into mxTidy an replace the value with the tidied value
        """
        if not value:   # XXX somehow submitting an empty textarea overwrites file uploads because empty strings end up here
            return
        field = self.getField('text')

        # hook for mxTidy / isTidyHtmlWithCleanup validator
        tidyOutput = self.getTidyOutput(field)
        if tidyOutput:
            value = tidyOutput

        field.set(self, value, **kwargs) # set is ok

    # XXX test me
    text_format = ComputedAttribute(ATCTContent.getContentType, 1)

    security.declarePrivate('guessMimetypeOfText')
    def guessMimetypeOfText(self):
        """For ftp/webdav upload: get the mimetype from the id and data
        """
        mtr  = getToolByName(self, 'mimetypes_registry')
        id   = self.getId()
        data = self.getRawText()
        ext  = id.split('.')[-1]

        if ext != id:
            mimetype = mtr.classify(data, filename=ext)
        else:
            # no extension
            mimetype = mtr.classify(data)

        if not mimetype or (type(mimetype) is TupleType and not len(mimetype)):
            # nothing found
            return None

        if type(mimetype) is TupleType and len(mimetype):
            mimetype = mimetype[0]
        return mimetype.normalized()

    security.declarePrivate('getTidyOutput')
    def getTidyOutput(self, field):
        """Get the tidied output for a specific field from the request
        if available
        """
        request = self.REQUEST
        tidyAttribute = '%s_tidier_data' % field.getName()
        if isinstance(request, HTTPRequest):
            return request.get(tidyAttribute, None)

    def _notifyOfCopyTo(self, container, op=0):
        """Override this to store a flag when we are copied, to be able
        to discriminate the right thing to do in manage_afterAdd here
        below.
        """
        self._v_renamed = 1
        return ATCTContent._notifyOfCopyTo(self, container, op=op)

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """Fix text when created througt webdav
        Guess the right mimetype from the id/data
        """
        ATCTContent.manage_afterAdd(self, item, container)
        field = self.getField('text')

        # hook for mxTidy / isTidyHtmlWithCleanup validator
        tidyOutput = self.getTidyOutput(field)
        if tidyOutput:
            if hasattr(self, '_v_renamed'):
                mimetype = field.getContentType(self)
                del self._v_renamed
            else:
                mimetype = self.guessMimetypeOfText()
            if mimetype:
                field.set(self, tidyOutput, mimetype=mimetype) # set is ok
            elif tidyOutput:
                field.set(self, tidyOutput) # set is ok

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, text_format, text, file='', safety_belt='', **kwargs):
        assert file == '', 'file currently not supported' # XXX
        self.setText(text, mimetype=translateMimetypeAlias(text_format))
        self.update(**kwargs)

registerType(ATDocument, PROJECTNAME)
