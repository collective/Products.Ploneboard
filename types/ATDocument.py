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

$Id: ATDocument.py,v 1.20 2004/06/03 02:24:21 tiran Exp $
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

from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.HistoryAware import HistoryAwareMixin
from Products.ATContentTypes.interfaces.IATDocument import IATDocument
from Products.ATContentTypes.types.schemata import ATDocumentSchema


class ATDocument(ATCTContent, HistoryAwareMixin):
    """An Archetypes derived version of CMFDefault's Document"""

    schema         =  ATDocumentSchema

    content_icon   = 'document_icon.gif'
    meta_type      = 'ATDocument'
    archetype_name = 'AT Document'
    immediate_view = 'document_view'
    default_view   = 'document_view'
    suppl_views    = ()
    newTypeFor     = ('Document', 'Document')
    typeDescription= 'Fill in the details of this document.'
    typeDescMsgId  = 'description_edit_document'
    assocMimetypes = ('application/pdf', 'application/xhtml+xml',
                      'application/msword', 'message/rfc822', 'text/*',
                     )
    assocFileExt   = ('doc', 'txt', 'stx', 'rst', 'rest', 'pdf', 'py' )

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
    
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'EditableBody')
    def EditableBody(self):
        """
        """
        return self.getRawText()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setText')
    def setText(self, value, **kwargs):
        """Body text mutator
        
        * hook into mxTidy an replace the value with the tidied value
        * set text_format for backward compatibility with std cmf types using setContentType
        
        """
        field = self.getField('text')

        # hook for mxTidy / isTidyHtmlWithCleanup validator
        tidyOutput = self.getTidyOutput(field)
        if tidyOutput:
            value = tidyOutput
        
        field.set(self, value, **kwargs)
        self.setContentType(kwargs.get('mimetype', None), skipField=True)

    security.declarePrivate('setContentType')
    def setContentType(self, mimetype, skipField=False):
        """Set the mime type of the text field and the text_format
        """
        if not mimetype:
            return
        
        if not skipField:
            field = self.getField('text')
            # AT lacks a setContentType() method :(
            bu = field.getRaw(self, raw=1)
            raw = bu.getRaw()
            filename, encoding = bu.filename, bu.original_encoding
            field.set(self, raw, mimetype=mimetype, filename=filename,
                      encoding=encoding)
        
        self.text_format = mimetype

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
        """get the tidied output for a specific field from the request if available
        """
        request = self.REQUEST
        tidyAttribute = '%s_tidier_data' % field.getName()
        if isinstance(request, HTTPRequest):
            return request.get(tidyAttribute, None)

    def _notifyOfCopyTo(self, container, op=0):
        """Overide this to store a flag when we are copied, to be able
        to discriminate the right thing to do in manage_afterAdd here
        below.
        """
        self._v_renamed = 1 

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """
        Fix text when created througt webdav
        Guess the right mimetype from the id/data
        """
        ATCTContent.manage_afterAdd(self, item, container)

        field    = self.getField('text')
        if hasattr(self, '_v_renamed'):
            mimetype = field.getContentType(self)
            del self._v_renamed
        else:
            mimetype = self.guessMimetypeOfText()

        # hook for mxTidy / isTidyHtmlWithCleanup validator
        tidyOutput = self.getTidyOutput(field)
        if tidyOutput and mimetype:
            field.set(self, tidyOutput, mimetype=mimetype)
        elif tidyOutput:
            field.set(self, tidyOutput)
        elif mimetype:
            self.setContentType(mimetype, skipField=False)

registerType(ATDocument, PROJECTNAME)
