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
""" Zope object encapsulating a controlled page templates that comes from the filesystem.

$Id: ControlledPageTemplateFile.py,v 1.3 2003/07/29 15:16:56 plonista Exp $
"""

import os
import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View
from Products.PageTemplates.PageTemplateFile import PageTemplateFile as BaseClass
from BaseControlledPageTemplate import BaseControlledPageTemplate
from utils import logException


class ControlledPageTemplateFile(BaseClass, BaseControlledPageTemplate):
    """Wrapper for Controlled Page Template"""
     
    meta_type = 'Controlled Page Template (File)'

    manage_options=(
        ({'label':'Customize', 'action':'manage_main'},
         {'label':'Test', 'action':'ZScriptHTML_tryForm'},
         {'label':'Validation','action':'manage_formValidatorsForm'},
         {'label':'Actions','action':'manage_formActionsForm'},
        ))

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, filename, _prefix=None, **kw):
        if not os.path.splitext(filename)[1]:
            filename = filename + '.cpt'
        self.filepath = filepath
        self._read_action_metadata(self.getId(), filepath)
        self._read_validator_metadata(self.getId(), filepath)
        return ControlledPageTemplateFile.inheritedAttribute('__init__')(self, filename, _prefix, **kw)


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


    def __call__(self, *args, **kwargs):
        return self._call(ControlledPageTemplateFile.inheritedAttribute('__call__'), *args, **kwargs)


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0
