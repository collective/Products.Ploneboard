import Globals
import AccessControl
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent, aq_chain, aq_self, Implicit
from Products.CMFCore.utils import getToolByName
from FormAction import FormAction
from globalVars import ANY_CONTEXT, ANY_BUTTON

class ControllerState(AccessControl.Role.RoleManager):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess('allow')

    id = None

    # The status variable used for determining state transitions
    status = 'success'

    # A set of i18n-friendly error messages.  Each key corresponds to a tuple
    # of the form (default_error_message, msgid), where msgid is used for i18n,
    # if present.
    errors = {}

    # The new context (use None if the context should remain the same)
    context = None

    # The button that was pressed (None if no named button was pressed)
    button = None

    # The default next action.  This can be overridden by values in the form
    # controller.
    next_action = None
    
    
    # A dict of variables including such things as portal_status_message.  Again,
    # each key corresponding to a message should have an i18n friendly value,
    # e.g. something like (id, default string) 
    kwargs = {}

    # a dict of ids of validators already executed
    _validators = {}

    def __init__(self, id=None, context=None, button=None, status='success', \
                 errors={}, next_action=None, **kwargs):
        self.setId(id)
        self.setButton(button)
        self.setStatus(status)
        self.setErrors(errors)
        self.setContext(context)
        self.setKwargs(kwargs)
        self.setNextAction(next_action)
        self._is_validating = 0
        self._validators = {}


    def set(self, **kwargs):
        """Set state object properties"""
        if kwargs.has_key('id'):
            self.setId(kwargs['id'])
            del kwargs['id']
        if kwargs.has_key('button'):
            self.setButton(kwargs['button'])
            del kwargs['button']
        if kwargs.has_key('status'):
            self.setStatus(kwargs['status'])
            del kwargs['status']
        if kwargs.has_key('errors'):
            self.setErrors(kwargs['errors'])
            del kwargs['errors']
        if kwargs.has_key('context'):
            self.setContext(kwargs['context'])
            del kwargs['context']
        if kwargs.has_key('next_action'):
            self.setNextAction(kwargs['next_action'])
            del kwargs['next_action']
        self.kwargs.update(kwargs)
        return self

        
    def setError(self, id, message, msgid=None, new_status=None):
        """Add an error message to the current state object.  The new_status
        argument allows you to optionally change the object's status."""
        self.errors[id] = (message, msgid)
        if new_status:
            self.status = new_status

    def getError(self, id):
        """Return the error message associated with the form variable id"""
        err = self.errors.get(id, None)
        if err:
            return err[0]
        return None
    
    def getI18NError(self, id):
        """Return the error message and i18n msgid associated with the form 
        variable id.  The return value is the tuple (errmsg, i18n_msgid)."""
        return self.errors.get(id, None)
        
    def getId(self):
        """Get the id of the calling script/page template"""
        return self.id

    def setId(self, id):
        """Set the id of the calling script/page template"""
        self.id = id

    def getButton(self):
        """Get the name of the named button pressed.  You can name a button NAME
        in a template by giving it the name form.button.NAME"""
        return self.button

    def setButton(self, button):
        """Set the name of the named button pressed.  You can name a button NAME
        in a template by giving it the name form.button.NAME"""
        self.button = button

    def getStatus(self):
        """Get the current status"""
        return self.status

    def setStatus(self, status):
        """Get the current status"""
        self.status = status

    def getErrors(self):
        """Return all errors in a dict of the form dict['name'] = errmsg"""
        err = {}
        for k in self.errors.keys():
            err[k] = self.errors[k][0]
        return err

    def getI18NErrors(self):
        """Return all errors in a dict of the form dict['name'] = (errmsg, i18n_msgid)"""
        return self.errors

    def setErrors(self, errors):
        """Set the error dictionary.  The dictionary should have entries of the
        form dict['name'] = (errmsg, i18n_msgid).  The msgid can be None"""
        self.errors = errors

    def getContext(self):
        """Get the context of the current form/script"""
        if self.context is None:
            return self.context
        return self.context[0]
        #return aq_inner(self.context)

    def setContext(self, context):
        """Set the context of the current form/script"""
        # Store the context in a list so that we don't nuke its acquisition chain.
        # This is kind of an evil hack, but since we aren't persisting 
        # ControllerState objects, it shouldn't cause any big problems.
        self.context = [context]
        # self.context = context

    def getKwargs(self):
        """Get any extra arguments (e.g. portal_status_message) that should be
        passed along to the next template/script"""
        return self.kwargs

    def setKwargs(self, kwargs):
        """Set any extra arguments (e.g. portal_status_message) that should be
        passed along to the next template/script"""
        self.kwargs = kwargs

    def getNextAction(self):
        """Get the default next action (this action can be overridden in 
        portal_form_controller).  The action will have the form 
        {'action_type':action_type, 'args':args} where action_type is a string
        (from portal_form_controller.validActionTypes), and args is a string 
        that will be passed to the constructor when generating an action object"""
        return self.next_action

    def setNextAction(self, action):
        """Set the default next action (this action can be overridden in 
        portal_form_controller).  setNextAction can be called either with a 
        dictionary argument of the form {'action_type':action_type, 'args':args}
        or with a string of the form 'action_type:args'.  Here action_type is a
        string (from form_controller.validActionTypes) and args is a string that
        will be passed to the constructor when generating an action object"""
        if action is None:
            self.next_action = action
            return
        if type(action) == type({}):
            action_type = action['action_type']
            args = action['args']
        else:
            split_action = action.split(':',1)
            action_type = split_action[0].strip()
            if len(split_action) == 2:
                args = split_action[1].strip()
            else:
                args = None
        controller = getToolByName(self.getContext(), 'portal_form_controller')
        if not action_type in controller.validActionTypes():
            raise KeyError, 'Unknown action type %s\n' % action_type
        self.next_action = FormAction(self.getId(), self.getStatus(), ANY_CONTEXT, ANY_BUTTON, action_type, args, controller)

    # indicate that a validator has been executed
    def _addValidator(self, validator):
        self._validators[validator] = 1
        
    # remove a validator from the list of already-executed validators
    def clearValidator(self, validator):
        if self._validators.has_key(validator):
            del self._validators[validator]

    # clear the list of already-executed validators
    def clearValidators(self):
        self._validators = {}
        
    # see if given validators have been executed
    def hasValidated(self, validators=[]):
        if validators is None:
            validators = []
        elif type(validators) != type([]):
            validators = [validators]
        for v in validators:
            if not self._validators.has_key(v):
                return 0
        return 1
        
    def _setValidating(self, is_validating):
        self._is_validating = is_validating
        
    def _isValidating(self):
        return self._is_validating

    def __str__(self):
        return 'id = %s\nstatus = %s\nbutton=%s\nerrors=%s\ncontext=%s\nkwargs=%s\nnext_action=%s\n' % \
            (self.id, str(self.getStatus()), str(self.getButton()), 
             str(self.getErrors()), str(self.getContext()), 
             str(self.kwargs), str(self.next_action))

Globals.InitializeClass(ControllerState)