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

$Id: FSControlledPythonScript.py,v 1.7 2003/09/12 22:49:03 tesdal Exp $
"""

import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.FSPythonScript import FSPythonScript as BaseClass
from ControlledPythonScript import ControlledPythonScript
from ControllerState import ControllerState
from ControlledBase import ControlledBase
from utils import logException

class FSControlledPythonScript (BaseClass, ControlledBase):
    """FSControlledPythonScripts act like Controlled Python Scripts but are not 
    directly modifiable from the management interface."""

    meta_type = 'Controlled Python Script'

    manage_options=(
           (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            {'label':'Actions','action':'manage_formActionsForm'},             
           ) + Cacheable.manage_options)


    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        BaseClass.__init__(self, id, filepath, fullname, properties)
        self.filepath = filepath
        self._read_action_metadata(self.getId(), filepath)


    def __call__(self, *args, **kwargs):
        result = FSControlledPythonScript.inheritedAttribute('__call__')(self, *args, **kwargs)
        if getattr(result, '__class__', None) == ControllerState and not result._isValidating():
            return self.getNext(result, self.REQUEST)
        return result


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, object, container):
        try:
            BaseClass.manage_afterAdd(self, object, container)
            # Re-read .metadata after adding so that we can do validation checks
            # using information in portal_form_controller.  Since manage_afterAdd
            # is not guaranteed to run, we also call these in __init__
            self._read_action_metadata(self.getId(), self.filepath)
        except:
            logException()
            raise


    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControlledPythonScript(self.getId())
        obj.write(self.read())
        return obj


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0

Globals.InitializeClass(FSControlledPythonScript)

registerFileExtension('cpy', FSControlledPythonScript)
registerMetaType('Controlled Python Script', FSControlledPythonScript)