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

$Id: ATDocument.py,v 1.7 2004/03/29 07:21:00 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

import difflib
from DateTime import DateTime
from OFS.History import historicalRevision
from DocumentTemplate.DT_Util import html_quote
from Acquisition import aq_parent

from Products.Archetypes.public import *
from Products.Archetypes.TemplateMixin import TemplateMixin
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.interfaces.IATDocument import IATDocument
from Products.ATContentTypes.types.schemata import ATDocumentSchema


class ATDocument(ATCTContent):
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

    __implements__ = ATCTContent.__implements__, IATDocument

    security       = ClassSecurityInfo()

    actions = updateActions(ATCTContent,
        ({
        'id'          : 'history',
        'name'        : 'History',
        'action'      : 'string:${object_url}/atdocument_history',
        'permissions' : (CMFCorePermissions.View,)
         },
        )
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
        
        * set text_format for backward compatibility with std cmf types
        """
        field = self.getField('text')

        # hook for mxTidy / isTidyHtmlWithCleanup validator
        tidyAttribute = '%s_tidier_data' % field.getName()
        tidyOutput    = self.REQUEST.get(tidyAttribute, None)
        if tidyOutput:
            value = tidyOutput
        
        field.set(self, value, **kwargs)

        # XXX not nice
        bu = self.getRawText(maybe_baseunit=1)
        if hasattr(bu, 'mimetype'):
            self.text_format = str(bu.mimetype)

registerType(ATDocument, PROJECTNAME)
