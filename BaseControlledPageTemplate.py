# ###########################################################################

import Globals
from AccessControl import ClassSecurityInfo
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.CMFCorePermissions import ManagePortal, View
from Products.CMFCore.utils import getToolByName
from ControlledBase import ControlledBase
from ControllerState import ControllerState
from ValidationError import ValidationError
from FormValidator import FormValidatorKey, FormValidator
from FormAction import FormActionKey, FormAction
from globalVars import ANY_CONTEXT, ANY_BUTTON

import sys
from urllib import quote


class BaseControlledPageTemplate(ControlledBase):

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    
    def _call(self, inherited_call, *args, **kwargs):
        # Intercept a call to a form and see if REQUEST.form contains the
        # value form.submitted.  If so, perform validation.  If not, update
        # the controller state and treat as a normal form.

        REQUEST = self.REQUEST

        controller = getToolByName(self, 'portal_form_controller')
        controller_state = controller.getState(self, is_validator=0)

        form_submitted = REQUEST.form.get('form.submitted', None)        
        if form_submitted:
            controller_state = self.getButton(controller_state)
            import pdb
            pdb.set_trace()
            validators = self.getValidators(controller_state).getValidators()
            controller_state = self.validate(controller_state, validators)
            del REQUEST.form['form.submitted']
            return self.getNext(controller_state)

        kwargs['state'] = controller_state
        return inherited_call(self, *args, **kwargs)


    def getButton(self, controller_state):
        controller_state.setButton(None)
        REQUEST = controller_state.getContext().REQUEST
        for k in REQUEST.form.keys():
            if k.startswith('form.button.'):
                controller_state.setButton(k[len('form.button.'):])
                return controller_state
        return controller_state
        

    def getValidators(self, controller_state):
        context = controller_state.getContext()
        REQUEST = context.REQUEST
        context_type = self._getTypeName(context)
        button = controller_state.getButton()
        controller = getToolByName(self, 'portal_form_controller')

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


    def _getTypeName(self, obj):
        type_name = getattr(obj, '__class__', None)
        if type_name:
            type_name = getattr(type_name, '__name__', None)
        return type_name


    def validate(self, controller_state, validators):
        context = controller_state.getContext()
        REQUEST = context.REQUEST
        if validators is None:
            REQUEST.set('controller_state', controller_state)
            return controller_state
        for v in validators:
            REQUEST.set('controller_state', controller_state)
            try:
                obj = context.restrictedTraverse(v)
                REQUEST = controller_state.getContext().REQUEST
                controller_state = mapply(obj, REQUEST.args, REQUEST,
                                          call_object, 1, missing_name, dont_publish_class,
                                          REQUEST, bind=1)

            except ValidationError, e:
                # if a validator raises a ValidatorException, execution of
                # validators is halted and the controller_state is set to
                # the controller_state embedded in the exception
                controller_state = e.controller_state
                state_class = getattr(controller_state, '__class__', None)
                if state_class != ControllerState:
                    raise Exception, 'Bad validator return type (%s)' % str(state_class)
                break
            state_class = getattr(controller_state, '__class__', None)
            if state_class != ControllerState:
                raise Exception, 'Bad validator return type from validator %s (%s)' % (str(v), str(state_class))
            REQUEST.set('controller_state', controller_state)

        REQUEST.set('controller_state', controller_state)
        return controller_state




Globals.InitializeClass(BaseControlledPageTemplate)