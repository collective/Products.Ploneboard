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

import os
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import getToolByName, expandpath
from Products.CMFCore.FSMetadata import FSMetadata, CMFConfigParser
from FormAction import FormActionType, FormAction, FormActionContainer
from FormValidator import FormValidator, FormValidatorContainer
from globalVars import ANY_CONTEXT, ANY_BUTTON

class ControllerBase:
    """Common functions for objects controlled by portal_form_controller"""
     
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ManagePortal, 'manage_formActionsForm')
    manage_formActionsForm = PageTemplateFile('www/manage_formActionsForm', globals())
    manage_formActionsForm.__name__ = 'manage_formActionsForm'

    security.declareProtected(ManagePortal, 'manage_formValidatorsForm')
    manage_formValidatorsForm = PageTemplateFile('www/manage_formValidatorsForm', globals())
    manage_formValidatorsForm.__name__ = 'manage_formValidatorsForm'


    security.declareProtected(ManagePortal, 'listActionTypes')
    def listActionTypes(self):
        """Return a list of available action types."""
        return getToolByName(self, 'portal_form_controller').listActionTypes()

    
    security.declareProtected(ManagePortal, 'listFormValidators')
    def listFormValidators(self, override, **kwargs):
        """Return a list of existing validators.  Validators can be filtered by
           specifying required attributes via kwargs"""
        controller = getToolByName(self, 'portal_form_controller')
        if override:
            return controller.validators.getFiltered(**kwargs)
        else:
            return self.validators.getFiltered(**kwargs)

        
    security.declareProtected(ManagePortal, 'listFormActions')
    def listFormActions(self, override, **kwargs):
        """Return a list of existing actions.  Actions can be filtered by
           specifying required attributes via kwargs"""
        controller = getToolByName(self, 'portal_form_controller')
        if override:
            return controller.actions.getFiltered(**kwargs)
        else:
            return self.actions.getFiltered(**kwargs)


    security.declareProtected(ManagePortal, 'listContextTypes')
    def listContextTypes(self):
        """Return list of possible types for template context objects"""
        return getToolByName(self, 'portal_form_controller').listContextTypes()


    security.declareProtected(ManagePortal, 'manage_editFormValidators')
    def manage_editFormValidators(self, REQUEST):
        """Process form validator edit form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.validators
        else:
            container = self.validators
        controller._editFormValidators(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declareProtected(ManagePortal, 'manage_addFormValidators')
    def manage_addFormValidators(self, REQUEST):
        """Process form validator add form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.validators
        else:
            container = self.validators
        controller._addFormValidators(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declareProtected(ManagePortal, 'manage_delFormValidators')
    def manage_delFormValidators(self, REQUEST):
        """Process form validator delete form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.validators
        else:
            container = self.validators
        controller._delFormValidators(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declareProtected(ManagePortal, 'manage_editFormActions')
    def manage_editFormActions(self, REQUEST):
        """Process form action edit form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.actions
        else:
            container = self.actions
        controller._editFormActions(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declareProtected(ManagePortal, 'manage_addFormAction')
    def manage_addFormAction(self, REQUEST):
        """Process form action add form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.actions
        else:
            container = self.actions
        controller._addFormAction(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declareProtected(ManagePortal, 'manage_delFormActions')
    def manage_delFormActions(self, REQUEST):
        """Process form action delete form"""
        controller = getToolByName(self, 'portal_form_controller')
        if REQUEST.form.get('override', 0):
            container = controller.actions
        else:
            container = self.actions
        controller._delFormActions(container, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    def getNext(self, controller_state, REQUEST):
        id = self.getId()
        status = controller_state.getStatus()
        context = controller_state.getContext()
        context_type = getattr(context, '__class__', None)
        if context_type:
            context_type = getattr(context_type, '__name__', None)
        button = controller_state.getButton()

        controller = getToolByName(self, 'portal_form_controller')

        next_action = None
        try:
            next_action = controller.actions.match(id, status, context_type, button)
        except ValueError:
            pass
        if next_action is None:
            try:
                next_action = self.actions.match(id, status, context_type, button)
            except ValueError:
                pass
            if next_action is None:
                next_action = controller_state.getNextAction()
                if next_action is None:
                    # default for failure is to traverse to the form
                    if status == 'failure':
                        next_action=FormAction(id, status, ANY_CONTEXT, ANY_BUTTON, 'traverse_to', 'string:%s' % id, controller)
                    if next_action is None:
                        metadata_actions = [str(a) for a in self.actions.getFiltered(object_id=id)]
                        zmi_actions = [str(a) for a in controller.actions.getFiltered(object_id=id)]
                        raise ValueError, 'No next action found for %s.%s.%s.%s\nMetadata actions:\n%s\n\nZMI actions:\n%s\n' % \
                            (id, status, context_type, button, '\n'.join(metadata_actions), '\n'.join(zmi_actions))

        REQUEST.set('controller_state', controller_state)
        return next_action.getAction()(controller_state)

    
    def getButton(self, controller_state, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('form.button.'):
                controller_state.setButton(k[len('form.button.'):])
                return controller_state
        return controller_state
        

    def getValidators(self, controller_state, REQUEST):
        controller = getToolByName(self, 'portal_form_controller')
        context = controller_state.getContext()
        context_type = controller._getTypeName(context)
        button = controller_state.getButton()

        validators = None
        try:
            validators = controller.validators.match(self.id, context_type, button)
            if validators is not None:
                return validators
        except ValueError:
            pass
        try:
            validators = self.validators.match(self.id, context_type, button)
            if validators is not None:
                return validators
        except ValueError:
            pass
        return FormValidator(self.id, ANY_CONTEXT, ANY_BUTTON, [])


    def _read_action_metadata(self, id, filepath):
        self.actions = FormActionContainer()
        
        metadata = FSMetadata(filepath)
        cfg = CMFConfigParser()
        filepath = expandpath(filepath)
        if os.path.exists(filepath + '.metadata'):
            cfg.read(filepath + '.metadata')
            
            try:
                controller = getToolByName(self, 'portal_form_controller')
            except AttributeError:
                controller = None

            actions = metadata._getSectionDict(cfg, 'actions')
            if actions is None:
                actions = {}
            for (k, v) in actions.items():
                # action.STATUS.CONTEXT_TYPE.BUTTON = ACTION_TYPE:ACTION_ARG
                component = k.split('.')
                while len(component) < 4:
                    component.append('')
                if component[0] != 'action':
                    raise ValueError, '%s: Format for .metadata actions is action.STATUS.CONTEXT_TYPE.BUTTON = ACTION_TYPE:ACTION_ARG (not %s)' % (filepath, k)
                act = v.split(':',1)
                while len(act) < 2:
                    act.append('')
                self.actions.set(FormAction(id, component[1], component[2], component[3], act[0], act[1], controller))


    def _read_validator_metadata(self, id, filepath):
        self.validators = FormValidatorContainer()
        
        metadata = FSMetadata(filepath)
        cfg = CMFConfigParser()
        filepath = expandpath(filepath)
        if os.path.exists(filepath + '.metadata'):
            cfg.read(filepath + '.metadata')
            
            try:
                controller = getToolByName(self, 'portal_form_controller')
            except AttributeError:
                controller = None
                
            validators = metadata._getSectionDict(cfg, 'validators')
            if validators is None:
                validators = {}
            for (k, v) in validators.items():
                # validators.CONTEXT_TYPE.BUTTON = LIST
                component = k.split('.')
                while len(component) < 3:
                    component.append('')
                if component[0] != 'validators':
                    raise ValueError, '%s: Format for .metadata validators is validators.CONTEXT_TYPE.BUTTON = LIST (not %s)' % (filepath, k)
                self.validators.set(FormValidator(id, component[1], component[2], v, controller))

    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 1
    
InitializeClass(ControllerBase)