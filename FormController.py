form_action_types = {}

import string
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.ObjectManager import bad_id
from Products.CMFCore.utils import getToolByName, UniqueObject, SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFFormController.ControllerState import ControllerState
from FormAction import FormActionType, FormActionKey, FormAction, FormActionContainer
from FormValidator import FormValidatorKey, FormValidator, FormValidatorContainer
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
                        {'label': 'Form Validators', 'action': 'manage_formValidatorsForm'},
                        {'label': 'Form Actions', 'action': 'manage_formActionsForm'},) +
                       SimpleItemWithProperties.manage_options)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/manage_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    security.declareProtected(ManagePortal, 'manage_formActionsForm')
    manage_formActionsForm = PageTemplateFile('www/manage_formActionsForm', globals())
    manage_formActionsForm.__name__ = 'manage_formActionsForm'

    security.declareProtected(ManagePortal, 'manage_formValidatorsForm')
    manage_formValidatorsForm = PageTemplateFile('www/manage_formValidatorsForm', globals())
    manage_formValidatorsForm.__name__ = 'manage_formValidatorsForm'

    # some aliases
    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = manage_overview

    security.declareProtected(ManagePortal, 'index_html')
    index_html = None

    def __init__(self):
        self.actions = FormActionContainer()
        self.validators = FormValidatorContainer()


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
                controller_state.setButton(None)
            controller_state.set(id=id, context=obj.getParentNode())
        else:
            if controller_state is None:
                raise ValueError, 'No controller state available'
        controller_state._setValidating(is_validator)
        self.REQUEST.set('controller_state', controller_state)
        return controller_state


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0

InitializeClass(FormController)
