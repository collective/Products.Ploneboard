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

$Id: FSControllerPythonScript.py,v 1.6 2003/10/24 18:40:56 plonista Exp $
"""

import re
import copy
import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import getToolByName
from Script import FSPythonScript as BaseClass
from ControllerPythonScript import ControllerPythonScript
from ControllerState import ControllerState
from ControllerBase import ControllerBase
from utils import logException


class FSControllerPythonScript (BaseClass, ControllerBase):
    """FSControllerPythonScripts act like Controller Python Scripts but are not 
    directly modifiable from the management interface."""

    meta_type = 'Filesystem Controller Python Script'

    manage_options=(
           (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            {'label':'Validation','action':'manage_formValidatorsForm'},
            {'label':'Actions','action':'manage_formActionsForm'},             
           ) + Cacheable.manage_options)

    is_validator = 0
    
    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        BaseClass.__init__(self, id, filepath, fullname, properties)
        self.filepath = filepath
        self._read_action_metadata(self.getId(), filepath)
        self._read_validator_metadata(self.getId(), self.filepath)


    def __call__(self, *args, **kwargs):
        REQUEST = self.REQUEST
        controller = getToolByName(self, 'portal_form_controller')
        controller_state = controller.getState(self, is_validator=0)
        controller_state = self.getButton(controller_state, REQUEST)
        validators = self.getValidators(controller_state, REQUEST).getValidators()
        controller_state = controller.validate(controller_state, REQUEST, validators)

        if controller_state.getStatus() == 'success':
            result = FSControllerPythonScript.inheritedAttribute('__call__')(self, *args, **kwargs)
            if getattr(result, '__class__', None) == ControllerState and not result._isValidating():
                return self.getNext(result, self.REQUEST)
            return result
        else:
            return self.getNext(controller_state, self.REQUEST)


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, object, container):
        try:
            BaseClass.manage_afterAdd(self, object, container)
            # Re-read .metadata after adding so that we can do validation checks
            # using information in portal_form_controller.  Since manage_afterAdd
            # is not guaranteed to run, we also call these in __init__
            self._read_action_metadata(self.getId(), self.filepath)
            self._read_validator_metadata(self.getId(), self.filepath)
        except:
            logException()
            raise

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControllerPythonScript(self.getId(), filepath=self.filepath)
        obj.write(self.read())
        obj.validators = copy.copy(self.validators)  # XXX - don't forget to enable this
        obj.actions = copy.copy(self.actions)
        return obj


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0

    def _getState(self):
        return getToolByName(self, 'portal_form_controller').getState(self, is_validator=0)


Globals.InitializeClass(FSControllerPythonScript)


registerFileExtension('cpy', FSControllerPythonScript)
registerMetaType('Controller Python Script', FSControllerPythonScript)