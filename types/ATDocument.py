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

$Id: ATDocument.py,v 1.8 2004/03/29 16:44:20 tiran Exp $
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

    security.declarePrivate('getHistories')
    def getHistories(self, max=10):
        """Get a list of historic revisions.
        
        Returns metadata as well    
        (object, time, transaction_note, user)"""
    
        historyList = self._p_jar.db().history(self._p_oid, None, max)
    
        if not historyList:
            return ()
    
        # Build list of objects
        lst = []
        parent = aq_parent(self)
        for revision in historyList:
            serial = revision['serial']
            # get the revision object and wrap it in a context wrapper
            obj    = historicalRevision(self, serial)
            obj    = obj.__of__(parent)
            lst.append((obj,
                        DateTime(revision['time']),
                        revision['description'],
                        revision['user_name'],
                      ))

        return lst

    security.declareProtected(CMFCorePermissions.View, 'getDocumentComparisons')
    def getDocumentComparisons(self, max=10, filterComment=0):
        """
        """
        mTool = getToolByName(self, 'portal_membership')
        
        histories = self.getHistories()
        if max > len(histories):
            max = len(histories)

        lst = []

        for revisivon in range(1, max):
    
            oldObj, oldTime, oldDesc, oldUser = histories[revisivon]
            newObj, newTime, newDesc, newUser = histories[revisivon-1]

            oldText  = oldObj.getRawText().split("\n")
            newText  = newObj.getRawText().split("\n")
            member = mTool.getMemberById(newUser)

            lines = [
                     html_quote(line)
                     for line in difflib.unified_diff(oldText, newText)
                    ][3:]

            description = newDesc            
            if filterComment:
                relativUrl = self.absolute_url(1)
                description = '<br />\n'.join(
                              [line
                               for line in description.split('\n')
                               if line.find(relativUrl) != -1]
                              )
            else:
                description.replace('\n', '<br />\n')
            
            if lines:
                lst.append({
                            'lines'       : lines,
                            'oldTime'     : oldTime,
                            'newTime'     : newTime,
                            'description' : description,
                            'user'        : newUser,
                            'member'      : member
                           })
        return lst

registerType(ATDocument, PROJECTNAME)
