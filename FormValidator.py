# ##############################################################################
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Key import Key
from globalVars import ANY_CONTEXT, ANY_BUTTON
from utils import log

_marker = []

# ##############################################################################
class FormValidatorKey(Key):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    
    def __init__(self, object_id, context_type, button, controller=None):
        object_id = object_id.strip()
        if controller:
            path_elements = object_id.split('/')
            for p in path_elements:
                s = controller._checkId(p)
                if s:
                    raise ValueError, 'Illegal template id: %s' % s

        if context_type:
            if controller:
                if not context_type in controller.listContextTypes():
                    log('Unknown context type %s for template %s' % (str(context_type), str(object_id)))
                    # Don't raise an exception because sometimes full list of
                    # types may be unavailable (e.g. when moving a site)
                    # raise ValueError, 'Illegal context type %s' % context_type
                    raise ValueError, 'Illegal context type %s' % context_type
        else:
            context_type = ANY_CONTEXT

        if button is not None:
            button = button.strip()
        if not button:
            button = ANY_BUTTON

        Key.__init__(self, (object_id, context_type, button))

    def getObjectId(self):
        return self.key[0]

    def getContextType(self):
        return self.key[1]
    
    def getButton(self):
        return self.key[2]
    
InitializeClass(FormValidatorKey)


# ##############################################################################
class FormValidator(SimpleItem):

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    
    def __init__(self, object_id, context_type, button, validators, controller=None):
        self.key = FormValidatorKey(object_id, context_type, button, controller)

        if type(validators) == type(''):
            validators = validators.split(',')
        validators = [v.strip() for v in validators if v]
        if controller:
            for v in validators:
                path_elements = v.split('/')
                for p in path_elements:
                    s = controller._checkId(p)
                    if s:
                        raise ValueError, 'Illegal template id: %s' % s
        self.validators = validators

    def __copy__(self):
        return FormValidator(self.getObjectId(), self.getContextType(), self.getButton(), self.getValidators())

    def getObjectId(self):
        return self.key.getObjectId()

    def getContextType(self):
        return self.key.getContextType()
    
    def getButton(self):
        return self.key.getButton()

    def getValidators(self):
        return self.validators
    
    def getKey(self):
        return self.key

InitializeClass(FormValidator)

# ##############################################################################
class FormValidatorContainer(SimpleItem):

    security = ClassSecurityInfo()
    security.setDefaultAccess('deny')

    def __init__(self):
        self.validators = {}
    
    def __copy__(self):
        newobj = FormValidatorContainer()
        for v in self.validators.values():
            newobj.set(v.__copy__())
        return newobj

    def set(self, validator):
        self.validators[validator.getKey()] = validator
        self._p_changed = 1
        
    def get(self, key):
        return self.validators[key]

    def delete(self, key):
        del self.validators[key]
        self._p_changed = 1
    
    def match(self, object_id, context_type, button):
        controller = getToolByName(self, 'portal_form_controller')
        validator = None
        try:
            validator = self.validators.get(FormValidatorKey(object_id, context_type, button, controller), None)
            if validator:
                return validator
        except ValueError:
            pass
        try:
            validator = self.validators.get(FormValidatorKey(object_id, ANY_CONTEXT, button, controller))
            if validator:
                return validator
        except ValueError:
            pass
        try:
            validator = self.validators.get(FormValidatorKey(object_id, context_type, ANY_BUTTON, controller))
            if validator:
                return validator
        except ValueError:
            pass
        try:
            return self.validators.get(FormValidatorKey(object_id, ANY_CONTEXT, ANY_BUTTON, controller), None)
        except ValueError:
            pass
        return None

    def getFiltered(self, object_id=_marker, context_type=_marker, 
                    button=_marker, validators=_marker):
        filtered = []
        keys = self.validators.keys()
        keys.sort()
        for key in keys:
            validator = self.validators[key]
            if object_id != _marker and not validator.getObjectId() == object_id:
                continue
            if context_type != _marker and not validator.getContextType() == context_type:
                continue
            if button != _marker and not validator.getButton() == button:
                continue
            if validators != _marker and not validator.getValidators() == validators:
                continue
            filtered.append(validator)
        return filtered
