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
""" Customizable validated page templates that come from the filesystem."""

import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal

from ValidatedPageTemplate import ValidatedPageTemplate

class FSValidatedPageTemplate(ValidatedPageTemplate):
    """Wrapper for Validated Page Template"""
     
    meta_type = 'Filesystem Validated Page Template'

    manage_options=(
        ({'label':'Customize', 'action':'manage_main'},
         {'label':'Test', 'action':'ZScriptHTML_tryForm'},
         {'label':'Validation','action':'manage_formValidatorsForm'},
         {'label':'Actions','action':'manage_formActionsForm'},
        ))

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ManagePortal, 'manage_formActionsForm')
    manage_formActionsForm = PageTemplateFile('www/manage_formActionsForm', globals())
    manage_formActionsForm.__name__ = 'manage_formActionsForm'

    security.declareProtected(ManagePortal, 'manage_formValidatorsForm')
    manage_formValidatorsForm = PageTemplateFile('www/manage_formValidatorsForm', globals())
    manage_formValidatorsForm.__name__ = 'manage_formValidatorsForm'


    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ValidatedPageTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        return obj

    security.declareProtected(ManagePortal, 'listActionTypes')
    def listActionTypes(self):
        """Return a list of available action types."""
        return getToolByName(self, 'form_controller').listActionTypes()
    
    security.declareProtected(ManagePortal, 'listFormValidators')
    def listFormValidators(self, **kwargs):
        """Return a list of existing validators.  Validators can be filtered by
           specifying required attributes via kwargs"""
        return getToolByName(self, 'form_controller').listFormValidators(**kwargs)
        
    security.declareProtected(ManagePortal, 'listFormActions')
    def listFormActions(self, **kwargs):
        """Return a list of existing actions.  Actions can be filtered by
           specifying required attributes via kwargs"""
        return getToolByName(self, 'form_controller').listFormActions(**kwargs)

    security.declareProtected(ManagePortal, 'listContextTypes')
    def listContextTypes(self):
        """Return list of possible types for template context objects"""
        return getToolByName(self, 'form_controller').listContextTypes()

    security.declareProtected(ManagePortal, 'manage_editFormValidators')
    def manage_editFormValidators(self, REQUEST):
        """Process form validator edit form"""
        getToolByName(self, 'form_controller').manage_editFormValidators(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')

    security.declareProtected(ManagePortal, 'manage_addFormValidators')
    def manage_addFormValidators(self, REQUEST):
        """Process form validator add form"""
        getToolByName(self, 'form_controller').manage_addFormValidators(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')

    security.declareProtected(ManagePortal, 'manage_delFormValidators')
    def manage_delFormValidators(self, REQUEST):
        """Process form validator delete form"""
        getToolByName(self, 'form_controller').manage_delFormValidators(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')

    security.declareProtected(ManagePortal, 'manage_editFormActions')
    def manage_editFormActions(self, REQUEST):
        """Process form action edit form"""
        getToolByName(self, 'form_controller').manage_editFormActions(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')

    security.declareProtected(ManagePortal, 'manage_addFormAction')
    def manage_addFormAction(self, REQUEST):
        """Process form action add form"""
        getToolByName(self, 'form_controller').manage_addFormAction(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')

    security.declareProtected(ManagePortal, 'manage_delFormActions')
    def manage_delFormActions(self, REQUEST):
        """Process form action delete form"""
        getToolByName(self, 'form_controller').manage_delFormActions(REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')

d = FSValidatedPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSValidatedPageTemplate)

registerFileExtension('vpt', FSValidatedPageTemplate)
registerMetaType('Validated Page Template', FSValidatedPageTemplate)