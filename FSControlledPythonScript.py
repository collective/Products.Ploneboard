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
##############################################################################
""" Customizable controlled python scripts that come from the filesystem.

$Id: FSControlledPythonScript.py,v 1.1 2003/07/04 20:11:59 plonista Exp $
"""

import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.FSPythonScript import FSPythonScript
from ControlledPythonScript import ControlledPythonScript
from ControlledBase import ControlledBase


class FSControlledPythonScript (FSPythonScript, ControlledBase):
    """FSControlledPythonScripts act like Controlled Python Scripts but are not 
    directly modifiable from the management interface."""

    meta_type = 'Controlled Python Script'

    manage_options=(
           (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            {'label':'Actions','action':'manage_formActionsForm'},             
           ))


    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControlledPythonScript(self.getId())
        obj.write(self.read())
        return obj


Globals.InitializeClass(FSControlledPythonScript)

registerFileExtension('cpy', FSControlledPythonScript)
registerMetaType('Controlled Python Script', FSControlledPythonScript)