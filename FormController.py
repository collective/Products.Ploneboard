from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.ObjectManager import bad_id
from Products.CMFCore.utils import getToolByName, UniqueObject, SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFFormController.ControllerState import ControllerState
import string

_marker = []
ANY_CONTEXT = None
ANY_BUTTON = None

form_action_types = {}
count = 0

def registerFormAction(id, factory, description=''):
    form_action_types[id] = {'factory':factory, 'description':description}


class FormController(UniqueObject, SimpleItemWithProperties):
    """ """

    security = ClassSecurityInfo()

    id = 'form_controller'
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
        self.form_actions = {}
        self.form_validators = {}


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

    def _compare(self, t1, t2):
        # make None end up last
        if t1 == None:
            return 1
        if t2 == None:
            return -1
        return cmp(t1, t2)


    def _compareKeys(self, t1, t2):
        for i in range(0, len(t1)-1):
            if t1[i] != t2[i]:
                return self._compare(t1[i], t2[i])
        return self._compare(t1[len(t1)-1], t2[len(t1)-1])


    # Web-accessible methods
    security.declareProtected(ManagePortal, 'listActionTypes')
    def listActionTypes(self):
        """Return a list of available action types."""
        keys = form_action_types.keys()
        keys.sort()
        action_types = []
        for k in keys:
            action_types.append({'id':k, 
                                 'factory':form_action_types[k]['factory'],
                                 'description':form_action_types[k]['description'],
                                })
        return action_types
    

    def validActionTypes(self):
        return form_action_types.keys()
 
    security.declareProtected(ManagePortal, 'listFormValidators')
    def listFormValidators(self, **kwargs):
        """Return a list of existing validators.  Validators can be filtered by
           specifying required attributes via kwargs"""
        keys = self.form_validators.keys()
        keys.sort(self._compareKeys)
        validators = []
        for k in keys:
            val_string = self.form_validators[k]
            if val_string == None:
                val_string = ''
            else:
                val_string = string.join(val_string, ', ')
                
            dict = {'template_id':k[0], 
                    'context_type':k[1], 
                    'button':k[2],
                    'validators':self.form_validators[k],
                    'st_validators':val_string
                   }
            append = 1
            for kw in kwargs.keys():
                if dict[kw] != kwargs[kw]:
                    append = 0
                    break
            if append:
                validators.append(dict)
        return validators
        
    
    security.declareProtected(ManagePortal, 'listFormActions')
    def listFormActions(self, **kwargs):
        """Return a list of existing actions.  Actions can be filtered by
           specifying required attributes via kwargs"""
        keys = self.form_actions.keys()
        keys.sort(self._compareKeys)
        actions = []
        for k in keys:
            dict = {'template_id':k[0], 
                    'status':k[1],
                    'context_type':k[2], 
                    'button':k[3],
                    'action_type':self.form_actions[k]['action_type'],
                    'args':self.form_actions[k]['args'],
                   }
            append = 1
            for kw in kwargs.keys():
                if dict[kw] != kwargs[kw]:
                    append = 0
                    break
            if append:
                actions.append(dict)
        return actions


    security.declareProtected(ManagePortal, 'listContextTypes')
    def listContextTypes(self):
        """Return list of possible types for template context objects"""
        types_tool = getToolByName(self, 'portal_types')
        return types_tool.listContentTypes()
        

    security.declareProtected(ManagePortal, 'manage_editFormValidators')
    def manage_editFormValidators(self, REQUEST):
        """Process form validator edit form"""
        n = len(self.form_validators.keys())
        self.form_validators.clear()
        for i in range(0, n):
            template_id = REQUEST.form.get('template_id_'+str(i))
            context_type = REQUEST.form.get('context_type_'+str(i))
            button = REQUEST.form.get('button_'+str(i))
            validators = REQUEST.form.get('validators_'+str(i))
            self.setValidators(template_id, context_type, button, validators)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declareProtected(ManagePortal, 'manage_addFormValidators')
    def manage_addFormValidators(self, REQUEST):
        """Process form validator add form"""
        template_id = REQUEST.form.get('new_template_id')
        context_type = REQUEST.form.get('new_context_type')
        button = REQUEST.form.get('new_button')
        validators = REQUEST.form.get('new_validators')
        self.setValidators(template_id, context_type, button, validators)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')


    security.declareProtected(ManagePortal, 'manage_delFormValidators')
    def manage_delFormValidators(self, REQUEST):
        """Process form validator delete form"""
        for i in range(0, len(self.form_validators.keys())):
            if REQUEST.form.get('del_id_'+str(i), None):
                del_template_id = REQUEST.form.get('del_template_id_'+str(i))
                del_context_type = REQUEST.form.get('del_context_type_'+str(i))
                del_button = REQUEST.form.get('del_button_'+str(i))
                self.delFormValidator(del_template_id, del_context_type, del_button)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formValidatorsForm')

    
    security.declareProtected(ManagePortal, 'setValidators')
    def setValidators(self, template_id, context_type, button, validators):
        template_id = template_id.strip()
        s = self._checkId(template_id)
        if s:
            raise ValueError, 'Illegal template id: %s' % s
        if context_type:
            if not context_type in self.listContextTypes():
                raise KeyError, 'Illegal context type %s' % context_type
        else:
            context_type = ANY_CONTEXT
        if button:
            button = button.strip()
        else:
            button = ANY_BUTTON
        if type(validators) == type(''):
            validators = validators.split(',')
        validators = [v.strip() for v in validators if v]
        for v in validators:
            s = self._checkId(v)
            if s:
                raise ValueError, 'Illegal validator id: %s' % s
        self.form_validators[(template_id, context_type, button)] = validators
        self._p_changed = 1


    security.declareProtected(ManagePortal, 'delFormValidator')
    def delFormValidator(self, template_id, context_type=_marker, button=_marker):
        if context_type != _marker and not context_type:
            context_type = ANY_CONTEXT
        if button != _marker and not button:
            button = ANY_BUTTON
        if context_type != _marker and button != _marker:
            del self.form_validators[(template_id, context_type, button)]
        else:
            for k in self.form_validators.keys():
                if k[0] != template_id:
                    continue
                if context_type != _marker and k[1] != context_type:
                    continue
                if button != _marker and k[2] != button:
                    continue
                del self.form_validators[k]      
        self._p_changed = 1


    security.declareProtected(ManagePortal, 'manage_editFormActions')
    def manage_editFormActions(self, REQUEST):
        """Process form action edit form"""
        n = len(self.form_actions.keys())
        self.form_actions.clear()
        for i in range(0, n):
            template_id = REQUEST.form.get('template_id_'+str(i))
            status = REQUEST.form.get('status_'+str(i)).strip()
            context_type = REQUEST.form.get('context_type_'+str(i)).strip()
            button = REQUEST.form.get('button_'+str(i)).strip()
            action_type = REQUEST.form.get('action_type_'+str(i)).strip()
            args = REQUEST.form.get('args_'+str(i)).strip()
            self.setAction(template_id, status, context_type, button, action_type, args)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declareProtected(ManagePortal, 'manage_addFormAction')
    def manage_addFormAction(self, REQUEST):
        """Process form action add form"""
        template_id = REQUEST.form.get('new_template_id')
        status = REQUEST.form.get('new_status').strip()
        context_type = REQUEST.form.get('new_context_type').strip()
        button = REQUEST.form.get('new_button').strip()
        action_type = REQUEST.form.get('new_action_type').strip()
        args = REQUEST.form.get('new_args').strip()
        self.setAction(template_id, status, context_type, button, action_type, args)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')


    security.declareProtected(ManagePortal, 'manage_delFormActions')
    def manage_delFormActions(self, REQUEST):
        """Process form action delete form"""
        for i in range(0, len(self.form_actions.keys())):
            if REQUEST.form.get('del_id_'+str(i), None):
                del_template_id = REQUEST.form.get('del_template_id_'+str(i))
                del_status = REQUEST.form.get('del_status_'+str(i))
                del_context_type = REQUEST.form.get('del_context_type_'+str(i))
                del_button = REQUEST.form.get('del_button_'+str(i))
                self.delFormAction(del_template_id, del_status, del_context_type, del_button)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_formActionsForm')

    
    security.declareProtected(ManagePortal, 'setAction')
    def setAction(self, template_id, status, context_type, button, action_type, args):
        template_id = template_id.strip()
        s = self._checkId(template_id)
        if s:
            raise ValueError, 'Illegal template id: %s' % s
        status = status.strip()
        if not status:
            raise ValueError, 'Illegal status %s' % (status)
        if context_type:
            if not context_type in self.listContextTypes():
                raise KeyError, 'Illegal context type %s' % context_type
        else:
            context_type = ANY_CONTEXT
        button = button.strip()
        if not button:
            button = ANY_BUTTON
        if not action_type in form_action_types.keys():
            raise ValueError, 'Illegal action type %s' % (action_type)
        if args is not None:
            args = args.strip()
        self.form_actions[(template_id, status, context_type, button)] = \
            {'action_type':action_type, 'args':args}
        self._p_changed = 1
    

    security.declareProtected(ManagePortal, 'delFormAction')
    def delFormAction(self, template_id, status=_marker, context_type=_marker, button=_marker):
        if context_type != _marker and not context_type:
            context_type = ANY_CONTEXT
        if button != _marker and not button:
            button = ANY_BUTTON
        if context_type != _marker and status != _marker and button != _marker:
            del self.form_actions[(template_id, status, context_type, button)]
        else:
            for k in self.form_actions.keys():
                if k[0] != template_id:
                    continue
                if status != _marker and k[1] != status:
                    continue
                if context_type != _marker and k[2] != context_type:
                    continue
                if button != _marker and k[3] != button:
                    continue
                del self.form_actions[k]
        self._p_changed = 1
        

    def getValidators(self, id, context_type, button):
        validators = self.form_validators.get((id, context_type, button), None)
        if validators is not None:
            return validators
        validators = self.form_validators.get((id, ANY_CONTEXT, button), None)
        if validators is not None:
            return validators
        validators = self.form_validators.get((id, context_type, ANY_BUTTON), None)
        if validators is not None:
            return validators
        return self.form_validators.get((id, ANY_CONTEXT, ANY_BUTTON), None)


    def getAction(self, id, status, context_type, button):
        action = self.form_actions.get((id, status, context_type, button), None)
        if action is not None:
#            import sys
#            sys.stdout.write('found %s for %s\n' % (action, str((id, status, context_type, button))))
            return action
        action = self.form_actions.get((id, status, ANY_CONTEXT, button), None)
        if action is not None:
#            import sys
#            sys.stdout.write('found %s for %s\n' % (action, str((id, status, ANY_CONTEXT, button))))
            return action
        action = self.form_actions.get((id, status, context_type, ANY_BUTTON), None)
        if action is not None:
#            import sys
#            sys.stdout.write('found %s for %s\n' % (action, str((id, status, context_type, ANY_BUTTON))))
            return action
#        import sys
#        sys.stdout.write('found %s for %s\n' % (self.form_actions.get((id, status, ANY_CONTEXT, ANY_BUTTON), None), str((id, status, ANY_CONTEXT, ANY_BUTTON))))
        return self.form_actions.get((id, status, ANY_CONTEXT, ANY_BUTTON), None)


    def getState(self, obj, is_validator):
        id = obj.id
        controller_state = self.REQUEST.get('controller_state', None)
        # Make sure controller_state is something generated by us, not something submitted via POST or GET
        if getattr(controller_state, '__class__', None) != ControllerState:
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
        self.REQUEST.set('controller_state', controller_state)
        return controller_state


    def getNext(self, controller_state):
        id = controller_state.getId()
        status = controller_state.getStatus()
        context = controller_state.getContext()
        REQUEST = context.REQUEST
        context_type = getattr(context, '__class__', None)
        if context_type:
            context_type = getattr(context_type, '__name__', None)
        button = controller_state.getButton()
        next_action = self.getAction(id, status, context_type, button)
        if next_action is None:
            next_action = controller_state.getNextAction()
            if next_action is None:
                raise ValueError, 'No next action found for %s.%s.%s.%s' % (id, status, context_type, button)
        REQUEST.set('controller_state', controller_state)
#        import sys
#        sys.stdout.write(str(next_action))
        action = form_action_types[next_action['action_type']]['factory'](next_action['args'])
        result = action(controller_state)
        if getattr(result, '__class__', None) == ControllerState:
            return self.getNext(result)
        return result


InitializeClass(FormController)