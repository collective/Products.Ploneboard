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

#        import sys
#        sys.stdout.write('\n\n------------------------------------------------\n')
#        sys.stdout.write('REQUEST form variables\n')
#        for k in REQUEST.form.keys():
#            sys.stdout.write('%s: %s\n' % (str(k), str(REQUEST.form[k])))

        form_controller = getToolByName(self, 'form_controller')
        controller_state = form_controller.getState(self, is_validator=0)

#        sys.stdout.write('\nInitial controller state:\n%s\n' % str(controller_state))

        form_submitted = REQUEST.form.get('form.submitted', None)
        
        if form_submitted:
            import sys
            
            controller_state = self.getButton(controller_state)
#            sys.stdout.write('getButton: %s\n' % str(controller_state))
            
            validators = self.getValidators(controller_state)
#            sys.stdout.write('validators = %s\n' % str(validators))
            controller_state = self.validate(controller_state, validators)
#            sys.stdout.write('validate: %s\n' % str(controller_state))
            controller_state = self.getDefaultAction(controller_state)
#            sys.stdout.write('default action: %s\n' % str(controller_state))
            self.cleanupRequest(REQUEST)
#            sys.stdout.write('cleanup: %s\n' % str(controller_state))
            return form_controller.getNext(controller_state)

        kwargs['state'] = controller_state
        return inherited_call(self, *args, **kwargs)


    def cleanupRequest(self, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('form.'):
                del REQUEST.form[k]


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
        form_controller = getToolByName(self, 'form_controller')
        validators = form_controller.getValidators(self.id, context_type, button)
        if validators is not None:
            return validators
        
        validators = REQUEST.form.get('form.validators.%s.%s' % (context_type, button), None)
        if validators is None:
            validators = REQUEST.form.get('form.validators.%s' % (context_type), None)
            if validators is None:
                validators = REQUEST.form.get('form.validators..%s' % (button), None)
                if validators is None:
                    validators = REQUEST.form.get('form.validators', None)
                    if validators is None:
                        return None
        validators = validators.split(',')
        return [v.strip() for v in validators if v]


    def getDefaultAction(self, controller_state):
        controller_state.setNextAction(None)
        status = controller_state.getStatus()
        context = controller_state.getContext()
        button = controller_state.getButton()
        REQUEST = context.REQUEST
        context_type = self._getTypeName(context)
        action = REQUEST.form.get('form.action.%s.%s.%s' % (status, context_type, button), None)
        if action is None:
            action = REQUEST.form.get('form.action.%s.%s' % (status, context_type), None)
            if action is None:
                action = REQUEST.form.get('form.action.%s..%s' % (status, button), None)
                if action is None:
                    action = REQUEST.form.get('form.action.%s' % (status), None)
                    if action is None:
                        # default for failure is to traverse to the form
                        if status == 'failure':
                            action='traverse_to:string:%s' % self.id
        if action is not None:
#            import sys
#            sys.stdout.write('action = %s\n' % action)
            controller_state.setNextAction(action)
        return controller_state
        

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
#            sys.stdout.write('controller_state = %s\n' % (str(controller_state)))
#            sys.stdout.write('Invoking %s\n' % v)
            try:
#                controller_state = context.restrictedTraverse(v)()

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