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

$Id: ATDocument.py,v 1.11 2004/04/02 21:30:26 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from types import TupleType

from ZPublisher.HTTPRequest import HTTPRequest

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
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
    suppl_views    = ()
    newTypeFor     = 'Document'
    TypeDescription= ''
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
        """Dummy attribute to allow drop-in replacement of Document"""
        return self.getText()

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

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """
        Fix text when created througt webdav
        Guess the right mimetype from the id/data
        """
        ATCTContent.manage_afterAdd(self, item, container)

        field    = self.getField('text')
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
