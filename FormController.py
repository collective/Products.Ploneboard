form_action_types = {}

import os, string
from AccessControl import ClassSecurityInfo
import Globals
from OFS.ObjectManager import bad_id
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from Products.CMFFormController import GLOBALS as fc_globals
from Products.CMFCore.utils import getToolByName, UniqueObject, SimpleItemWithProperties, format_stx
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFFormController.ControllerState import ControllerState
from FormAction import FormActionType, FormActionKey, FormAction, FormActionContainer
from FormValidator import FormValidatorKey, FormValidator, FormValidatorContainer
from ValidationError import ValidationError
from globalVars import ANY_CONTEXT, ANY_BUTTON

_marker = []

def registerFormAction(id, factory, description=''):
    form_action_types[id] = FormActionType(id, factory, description)


class FormController(UniqueObject, SimpleItemWithProperties):
    """ """

    security = ClassSecurityInfo()

    id = 'portal_form_controller'
    title = 'Manage form validation and post-validation actions'
    meta_type= 'Form Controller Tool'

    manage_options = ( ({'label':'Overview', 'action':'manage_overview'},
                        {'label':'Documentation', 'action':'manage_docs'},
                        {'label': 'Validation', 'action': 'manage_formValidatorsForm'},
                        {'label': 'Actions', 'action': 'manage_formActionsForm'},) +
                       SimpleItemWithProperties.manage_options)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile(os.path.join('www','manage_overview'), globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    security.declareProtected(ManagePortal, 'manage_docs')
    manage_docs = PageTemplateFile(os.path.join('www','manage_docs'), globals())
    manage_docs.__name__ = 'manage_docs'

    security.declareProtected(ManagePortal, 'manage_formActionsForm')
    manage_formActionsForm = PageTemplateFile(os.path.join('www','manage_formActionsForm'), globals())
    manage_formActionsForm.__name__ = 'manage_formActionsForm'

    security.declareProtected(ManagePortal, 'manage_formValidatorsForm')
    manage_formValidatorsForm = PageTemplateFile(os.path.join('www','manage_formValidatorsForm'), globals())
    manage_formValidatorsForm.__name__ = 'manage_formValidatorsForm'

    # some aliases
    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = manage_overview

    security.declareProtected(ManagePortal, 'index_html')
    index_html = None

    wwwpath = os.path.join(Globals.package_home(fc_globals), 'www')
    f = open(os.path.join(wwwpath, 'docs.stx'), 'r')
    _docs = f.read()
    f.close()
    _docs = format_stx(_docs)


    def __init__(self):
        self.actions = FormActionContainer()
        self.validators = FormValidatorContainer()


    security.declarePublic('docs')
    def docs(self):
        """Returns FormController docs formatted as HTML"""
        return self._docs


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, object, container):
        portal = getToolByName(object, 'portal_url').getPortalObject()
        object.plone = portal.__class__.__name__ == 'PloneSite'
        SimpleItemWithProperties.manage_afterAdd(self, object, container)


    def view(self, REQUEST, RESPONSE):
        """Invokes the default view."""
        return self.__call__(REQUEST, RESPONSE)


    def __call__(self, REQUEST, RESPONSE):
        """Invokes the default view."""
        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_main' % self.absolute_url())


    def _checkId(self, id):
        """See if an id is valid CMF/Plone id"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        if not id:
            return 'Empty id'
        s = bad_id(id)
        if s:
            return '\'%s\' is not a valid id' % (id)
        if self.plone:
            if hasattr(portal, 'portal_properties') and \
                hasattr(portal.portal_properties, 'site_properties') and \
                hasattr(portal.portal_properties.site_properties, 'invalid_ids'):
                    if id in portal.portal_properties.site_properties.invalid_ids:
                        return '\'%s\' is a reserved id' % (id)


    # Web-accessible methods
    security.declareProtected(ManagePortal, 'listActionTypes')
    def listActionTypes(self):
        """Return a list of available action types."""
        keys = form_action_types.keys()
        keys.sort()
        action_types = []
        for k in keys:
            action_types.append(form_action_types.get(k))
        return action_types


    def validActionTypes(self):
        return form_action_types.keys()


    security.declareProtected(ManagePortal, 'listContextTypes')
    def listContextTypes(self):
        """Return list of possible types for template context objects"""
        types_tool = getToolByName(self, 'portal_types')
        return types_tool.listContentTypes()


    security.declareProtected(ManagePortal, 'listFormValidators')
    def listFormValidators(self, override, **kwargs):
        """Return a list of existing validators.  Validators can be filtered by
           specifying required attributes via kwargs"""
        return self.validators.getFiltered(**kwargs)


    security.declareProtected(ManagePortal, 'listFormActions')
    def listFormActions(self, override, **kwargs):
        """Return a list of existing actions.  Actions can be filtered by
           specifying required attributes via kwargs"""
        return self.actions.getFiltered(**kwargs)


    security.declareProtected(ManagePortal, 'manage_editFormValidators')
    def manage_editFormValidators(self, REQUEST):
        """Process form validator edit form"""
        self._editFormValidators(self.validators, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declarePrivate('_editFormValidators')
    def _editFormValidators(self, container, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('old_object_id_'):
                n = k[len('old_object_id_'):]
                old_object_id = REQUEST.form.get('old_object_id_'+n)
                old_context_type = REQUEST.form.get('old_context_type_'+n)
                old_button = REQUEST.form.get('old_button_'+n)
                container.delete(FormValidatorKey(old_object_id, old_context_type, old_button, self))
                object_id = REQUEST.form.get('object_id_'+n)
                context_type = REQUEST.form.get('context_type_'+n)
                button = REQUEST.form.get('button_'+n)
                validators = REQUEST.form.get('validators_'+n)
                container.set(FormValidator(object_id, context_type, button, validators, self))


    # Method for programmatically adding validators
    security.declareProtected(ManagePortal, 'addFormValidators')
    def addFormValidators(self, object_id, context_type, button, validators):
        self.validators.set(FormValidator(object_id, context_type, button, validators, self))


    security.declareProtected(ManagePortal, 'manage_addFormValidators')
    def manage_addFormValidators(self, REQUEST):
        """Process form validator add form"""
        self._addFormValidators(self.validators, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declarePrivate('_addFormValidators')
    def _addFormValidators(self, container, REQUEST):
        object_id = REQUEST.form.get('new_object_id')
        context_type = REQUEST.form.get('new_context_type')
        button = REQUEST.form.get('new_button')
        validators = REQUEST.form.get('new_validators')
        container.set(FormValidator(object_id, context_type, button, validators, self))


    security.declareProtected(ManagePortal, 'manage_delFormValidators')
    def manage_delFormValidators(self, REQUEST):
        """Process form validator delete form"""
        self._delFormValidators(self.validators, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declarePrivate('_delFormValidators')
    def _delFormValidators(self, container, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('del_id_'):
                n = k[len('del_id_'):]
                old_object_id = REQUEST.form.get('old_object_id_'+n)
                old_context_type = REQUEST.form.get('old_context_type_'+n)
                old_button = REQUEST.form.get('old_button_'+n)
                container.delete(FormValidatorKey(old_object_id, old_context_type, old_button, self))


    security.declareProtected(ManagePortal, 'manage_editFormActions')
    def manage_editFormActions(self, REQUEST):
        """Process form action edit form"""
        self._editFormActions(self.actions, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declarePrivate('_editFormActions')
    def _editFormActions(self, container, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('old_object_id_'):
                n = k[len('old_object_id_'):]
                old_object_id = REQUEST.form.get('old_object_id_'+n)
                old_status = REQUEST.form.get('old_status_'+n)
                old_context_type = REQUEST.form.get('old_context_type_'+n)
                old_button = REQUEST.form.get('old_button_'+n)
                container.delete(FormActionKey(old_object_id, old_status, old_context_type, old_button, self))
                object_id = REQUEST.form.get('object_id_'+n)
                status = REQUEST.form.get('status_'+n)
                context_type = REQUEST.form.get('context_type_'+n)
                button = REQUEST.form.get('button_'+n)
                action_type = REQUEST.form.get('action_type_'+n)
                action_arg = REQUEST.form.get('action_arg_'+n)
                container.set(FormAction(object_id, status, context_type, button, action_type, action_arg, self))


    # Method for programmatically adding actions
    security.declareProtected(ManagePortal, 'addFormAction')
    def addFormAction(self, object_id, status, context_type, button, action_type, action_arg):
        self.actions.set(FormAction(object_id, status, context_type, button, action_type, action_arg, self))


    security.declareProtected(ManagePortal, 'manage_addFormAction')
    def manage_addFormAction(self, REQUEST):
        """Process form action add form"""
        self._addFormAction(self.actions, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declarePrivate('_addFormAction')
    def _addFormAction(self, container, REQUEST):
        object_id = REQUEST.form.get('new_object_id')
        status = REQUEST.form.get('new_status').strip()
        context_type = REQUEST.form.get('new_context_type').strip()
        button = REQUEST.form.get('new_button').strip()
        action_type = REQUEST.form.get('new_action_type').strip()
        action_arg = REQUEST.form.get('new_action_arg').strip()
        container.set(FormAction(object_id, status, context_type, button, action_type, action_arg, self))


    security.declareProtected(ManagePortal, 'manage_delFormActions')
    def manage_delFormActions(self, REQUEST):
        """Process form action delete form"""
        self._delFormActions(self.actions, REQUEST)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declarePrivate('_delFormAction')
    def _delFormActions(self, container, REQUEST):
        for k in REQUEST.form.keys():
            if k.startswith('del_id_'):
                n = k[len('del_id_'):]
                old_object_id = REQUEST.form.get('old_object_id_'+n)
                old_status = REQUEST.form.get('old_status_'+n)
                old_context_type = REQUEST.form.get('old_context_type_'+n)
                old_button = REQUEST.form.get('old_button_'+n)
                container.delete(FormActionKey(old_object_id, old_status, old_context_type, old_button, self))


    def getValidators(self, object_id, context_type, button):
        return self.validators.match(id, context_type, button)


    def getAction(self, id, status, context_type, button):
        return self.actions.match(id, status, context_type, button)


    def getState(self, obj, is_validator):
        id = obj.id
        controller_state = self.REQUEST.get('controller_state', None)
        # The variable 'env' is a dictionary that is passed
        # along using record variables on forms so that you can keep
        # some state between different forms.
        env = self.REQUEST.get('form_env', {})
        # Make sure controller_state is something generated by us, not something submitted via POST or GET
        if controller_state and getattr(controller_state, '__class__', None) != ControllerState:
            controller_state = None

        if not is_validator:
            # Construct a new controller state object or clear out the existing
            # one unless we are in a validator script.
            if controller_state is None:
                # XXX - errors={} shouldn't need to be set here, but without it
                # I encountered what looks like a weird Zope caching bug.
                # To reproduce, install CMFFormControllerDemo, go to portal_skins
                # then to CMFFormControllerDemo, then click on test_form and
                # click the Test tab.  Submit the form with an empty text box.
                # Now back up to the ZMI and click the Test tab again.  If
                # errors={} is left out in the line below, ControllerState.__init__()
                # gets called with errors set to a non-empty value (more
                # precisely, it is set to the value that was in REQUEST.controller_state.
                # Yikes!
                controller_state = ControllerState(errors={})
            else:
                # clear out values we don't want to carry over from previous states.
                controller_state.setStatus('success')
                controller_state.setNextAction(None)
                #controller_state.setButton(None)
            controller_state.set(id=id, context=obj.getParentNode())
        else:
            if controller_state is None:
                raise ValueError, 'No controller state available.  ' + \
                    'This commonly occurs when a ControllerValidator (.vpy) ' + \
                    'script is invoked via the validation mechanism in the ' + \
                    'portal_form tool.  If you are using a package designed to ' + \
                    'be used with portal_form, you are probably inadvertently ' + \
                    'invoking a validator designed for use with CMFFormController (e.g. validate_id).  ' + \
                    'If you are using a package designed to be used with CMFFormController, you probably ' + \
                    'have a "portal_form" in your URL that needs to be removed.'
        controller_state._setValidating(is_validator)
        # Pass environment along, with care so we don't override
        # existing variables.
        for k, v in env.items():
            controller_state.kwargs.setdefault(k, v)
        self.REQUEST.set('controller_state', controller_state)
        return controller_state


    def validate(self, controller_state, REQUEST, validators, argdict=None):
        if argdict is None:
            args = REQUEST.args
            kwargs = REQUEST
        else:
            args = ()
            if REQUEST is None:
                kwargs = argdict
            else:
                kwargs = {}
                for k, v in REQUEST.items():
                    kwargs[k] = v
                kwargs.update(argdict)
        context = controller_state.getContext()
        if validators is None:
            REQUEST.set('controller_state', controller_state)
            return controller_state
        for v in validators:
            REQUEST.set('controller_state', controller_state)
            if controller_state.hasValidated(v):
                continue
            try:
                # make sure validator exists
                obj = context.restrictedTraverse(v, default=None)
                if obj is None:
                    raise ValueError, 'Unable to find validator %s\n' % str(v)
                if not getattr(obj, 'is_validator', 1):
                    raise ValueError, '%s is not a CMFFormController validator' % str(v)
                REQUEST = controller_state.getContext().REQUEST
                controller_state = mapply(obj, args, kwargs,
                                          call_object, 1, missing_name, dont_publish_class,
                                          REQUEST, bind=1)
                if controller_state is None or getattr(controller_state, '__class__', None) != ControllerState:
                    raise ValueError, 'Validator %s did not return the state object' % str(v)
                controller_state._addValidator(v)
            except ValidationError, e:
                # if a validator raises a ValidatorException, execution of
                # validators is halted and the controller_state is set to
                # the controller_state embedded in the exception
                controller_state = e.controller_state
                state_class = getattr(controller_state, '__class__', None)
                if state_class != ControllerState:
                    raise Exception, 'Bad ValidationError state (type = %s)' % str(state_class)
                break
            state_class = getattr(controller_state, '__class__', None)
            if state_class != ControllerState:
                raise Exception, 'Bad validator return type from validator %s (%s)' % (str(v), str(state_class))
            REQUEST.set('controller_state', controller_state)

        REQUEST.set('controller_state', controller_state)
        return controller_state


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0


    def _getTypeName(self, obj):
        type_name = getattr(obj, '__class__', None)
        if type_name:
            type_name = getattr(type_name, '__name__', None)
        return type_name


Globals.InitializeClass(FormController)
