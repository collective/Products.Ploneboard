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

$Id: FSControllerPageTemplate.py,v 1.6 2003/12/02 16:24:42 plonista Exp $
"""

import copy
import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import expandpath
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.FSPageTemplate import FSPageTemplate as BaseClass
from BaseControllerPageTemplate import BaseControllerPageTemplate
from ControllerPageTemplate import ControllerPageTemplate
from ControllerBase import ControllerBase
from FormAction import FormActionContainer
from FormValidator import FormValidatorContainer
from utils import log, logException


class FSControllerPageTemplate(BaseClass, BaseControllerPageTemplate):
    """Wrapper for Controller Page Template"""
     
    meta_type = 'Filesystem Controller Page Template'

    manage_options=(
        ({'label':'Customize', 'action':'manage_main'},
         {'label':'Test', 'action':'ZScriptHTML_tryForm'},
         {'label':'Validation','action':'manage_formValidatorsForm'},
         {'label':'Actions','action':'manage_formActionsForm'},
        ) + Cacheable.manage_options)

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)


    def __init__(self, id, filepath, fullname=None, properties=None):
        BaseClass.__init__(self, id, filepath, fullname, properties)
        self.filepath = filepath
        try:
            self._read_action_metadata(self.getId(), filepath)
            self._read_validator_metadata(self.getId(), filepath)
        except ValueError, e:
            log(summary='metadata error', text='file = %s' % filepath)
            raise


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
            log(summary='metadata error', text='file = %s' % self.filepath)
            logException()
            raise


    def __call__(self, *args, **kwargs):
        return self._call(FSControllerPageTemplate.inheritedAttribute('__call__'), *args, **kwargs)


    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControllerPageTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        obj.validators = copy.copy(Acquisition.aq_base(self.validators))
        obj.actions = copy.copy(Acquisition.aq_base(self.actions))
        return obj


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0


d = FSControllerPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSControllerPageTemplate)

registerFileExtension('cpt', FSControllerPageTemplate)
registerMetaType('Controller Page Template', FSControllerPageTemplate)