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

Inspired by CMFDynamicDocument from Andrew:
  http://www.zope.org/Members/ensane/CMFDynamicDocument

$Id: ATDynDocument.py,v 1.1 2004/04/22 23:26:58 tiran Exp $
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
from Products.ATContentTypes.types.ATDocument import ATDocument
from Products.ATContentTypes.interfaces.IATDynDocument import IATDynDocument
from Products.ATContentTypes.types.schemata import ATDynDocumentSchema

from Acquisition import Implicit, aq_parent, aq_inner
from TAL.TALDefs import TALESError
from AccessControl import getSecurityManager
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import SecureModuleImporter

ptBody="""
<tal:body metal:use-macro="%s">
<div metal:fill-slot="%s">
%s
</div>
</tal:body>
"""

translate = [
    ('&amp;', '&'), 
    ('&lt;', '<'), 
    ('&gt;', '>'), 
]

class DynamicPageTemplate(PageTemplate, Implicit):
    """Dynamic page template for ATDynDocument
    """

    def pt_getContext(self):
        root = self.getPhysicalRoot()
        template = aq_parent(self)
        here = aq_parent(template)
        c = {'template': template,
             'document': template,
             'options': {},
             'nothing': None,
             'root': root,
             'request': getattr(root, 'REQUEST', None),
             'modules': SecureModuleImporter,
             'here': here,
             'context': here,
             'container': aq_inner(here),
             }
        return c

class ATDynDocument(ATDocument):
    """An Archetypes baed Document with TAL support"""

    schema         =  ATDynDocumentSchema

    content_icon   = 'document_icon.gif'
    meta_type      = 'ATDynDocument'
    archetype_name = 'AT Dyn Document'
    immediate_view = 'document_view'
    suppl_views    = ()
    newTypeFor     = ''
    typeDescription= 'Fill in the details of this document.'
    typeDescMsgId  = 'description_edit_document'
    assocMimetypes = ()
    assocFileExt   = ()

    __implements__ = (ATDocument.__implements__,
                      IATDynDocument,
                     )

    security       = ClassSecurityInfo()

    #actions = updateActions(ATDocument
    #                       )
    
    security.declarePrivate('getRawPT')
    def getRawPT(self):
        """Return a context but unrendered wrapper page template
        """
        pt = DynamicPageTemplate().__of__(self)
##        template = self.getTemplateMacro()
##        slot     = self.getSlot()
##        text     = self.getRawText()
##        ptData   = ptBody % (template, slot, text)
        ptData = self.getRawText()
        pt.write(ptData)
        return pt

    security.declarePrivate('getPT')
    def getPT(self):
        """Get the full rendered page template
        """
        security = getSecurityManager()
        security.addContext(self)
        user = security.getUser()
        pt = self.getRawPT()
        
        try:
            try:
                result = pt.pt_render(extra_context={'user': user})
            except TALESError, err:
                if err.type == 'Unauthorized':
                    raise err.type, err.value, err.traceback
                raise
            return result
        finally:
            security.removeContext(self)
        
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setText')
    def setText(self, value, **kwargs):
        """Body text mutator
        
        * set text_format for backward compatibility with std cmf types using setContentType
        
        """
        field = self.getField('text')
        field.set(self, value, **kwargs)
        self.setContentType(kwargs.get('mimetype', None), skipField=True)

    security.declareProtected(CMFCorePermissions.View, 'getText')
    def getText(self):
        """Get the rendered body text
        """
        mt = self.getContentType()
        pt = self.getPT()
        if mt not in ('text/html',):
            tField = self.getField('text')
            out    = tField.default_output_type
            ptTool = getToolByName(self, 'portal_transforms')
            result = ptTool.convertTo(out, pt, mimetype=mt).getData()
        else:
            result = pt

        # replace quoted html entities by unquoted
        if mt not in ('text/html', 'text/plain', 'text/plain-pre'):
            for key,val in translate:
                result = result.replace(key, val)            
        
        return result

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """Overwrite it
        """
        ATCTContent.manage_afterAdd(self, item, container)


registerType(ATDynDocument, PROJECTNAME)
