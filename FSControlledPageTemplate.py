##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##########################################################################
""" Customizable validated page templates that come from the filesystem.

$Id: FSControlledPageTemplate.py,v 1.1 2003/07/04 20:11:59 plonista Exp $
"""

from Products.CMFCore.FSPageTemplate import FSPageTemplate as BaseClass
import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from ControlledPageTemplate import ControlledPageTemplate
from ControlledBase import ControlledBase
from BaseControlledPageTemplate import BaseControlledPageTemplate


class FSControlledPageTemplate(BaseClass, BaseControlledPageTemplate):
    """Wrapper for Controlled Page Template"""
     
    meta_type = 'Filesystem Controlled Page Template'

    manage_options=(
        ({'label':'Customize', 'action':'manage_main'},
         {'label':'Test', 'action':'ZScriptHTML_tryForm'},
         {'label':'Validation','action':'manage_formValidatorsForm'},
         {'label':'Actions','action':'manage_formActionsForm'},
        ))

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __call__(self, *args, **kwargs):
        return self._call(FSControlledPageTemplate.inheritedAttribute('__call__'), *args, **kwargs)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControlledPageTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        return obj


d = FSControlledPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSControlledPageTemplate)

registerFileExtension('cpt', FSControlledPageTemplate)
registerMetaType('Controlled Page Template', FSControlledPageTemplate)