# ##############################################################################
import copy
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Key import Key
from globalVars import ANY_CONTEXT, ANY_BUTTON

_marker = []

# ##############################################################################
class FormActionType(SimpleItem):

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, id, factory, description):
        self.id = id
        self.factory = factory
        self.description = description
        
    def getId(self):
        return self.id
    
    def getFactory(self):
        return self.factory
    
    def getDescription(self):
        return self.description

InitializeClass(FormActionType)

# ##############################################################################
class FormActionKey(Key):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    
    def __init__(self, object_id, status, context_type, button, controller=None):
        object_id = object_id.strip()
        if controller:
            s = controller._checkId(object_id)
            if s:
                raise ValueError, 'Illegal template id: %s' % s

        status = status.strip()
        if not status:
            raise ValueError, 'Illegal status %s' % (status)

        if context_type:
            if controller:
                if not context_type in controller.listContextTypes():
                    raise ValueError, 'Illegal context type %s' % context_type
        else:
            context_type = ANY_CONTEXT

        if button is not None:
            button = button.strip()
        if not button:
            button = ANY_BUTTON

        Key.__init__(self, (object_id, status, context_type, button))

    def getObjectId(self):
        return self.key[0]

    def getStatus(self):
        return self.key[1]
    
    def getContextType(self):
        return self.key[2]
    
    def getButton(self):
        return self.key[3]
    
InitializeClass(FormActionKey)


# ##############################################################################
class FormAction(SimpleItem):

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    
    def __init__(self, object_id, status, context_type, button, 
                 action_type, action_arg, controller=None):
        from FormController import form_action_types

        self.key = FormActionKey(object_id, status, context_type, button,
                                 controller)
        self.action_type = action_type
        self.action_arg = action_arg

        if not form_action_types.has_key(action_type):
            raise ValueError, 'Illegal action type %s for %s' % (action_type, object_id)
        if action_arg is not None:
            action_arg = action_arg.strip()
        self.action = form_action_types[action_type].getFactory()(action_arg)

    def getKey(self):
        return self.key
    
    def getObjectId(self):
        return self.key.getObjectId()

    def getStatus(self):
        return self.key.getStatus()
    
    def getContextType(self):
        return self.key.getContextType()
    
    def getButton(self):
        return self.key.getButton()

    def getActionType(self):
        return self.action_type
    
    def getActionArg(self):
        return self.action_arg

    def getAction(self):
        return self.action

InitializeClass(FormAction)

# ##############################################################################
class FormActionContainer(SimpleItem):

    security = ClassSecurityInfo()
    security.setDefaultAccess('deny')

    def __init__(self):
        self.actions = {}
    
    def set(self, action):
        self.actions[action.getKey()] = action
        self._p_changed = 1
        
    def get(self, key):
        return self.actions[key]

    def delete(self, key):
        del self.actions[key]
        self._p_changed = 1
    
    def match(self, object_id, status, context_type, button):
        controller = getToolByName(self, 'portal_form_controller')
        action = None
        try:
            action = self.actions.get(FormActionKey(object_id, status, \
                                        context_type, button, controller), None)
            if action:
                return action
        except ValueError:
            pass
        try:
            action = self.actions.get(FormActionKey(object_id, status, \
                                            ANY_CONTEXT, button, controller), None)
            if action:
                return action
        except ValueError:
            pass
        try:
            action = self.actions.get(FormActionKey(object_id, status, \
                                            context_type, ANY_BUTTON, controller), None)
            if action:
                return action
        except ValueError:
            pass
        try:
            return self.actions.get(FormActionKey(object_id, status, \
                                            ANY_CONTEXT, ANY_BUTTON, controller), None)
        except ValueError:
            pass
        return None

    def getFiltered(self, object_id=_marker, status=_marker, context_type=_marker, 
                    button=_marker, action_type=_marker, action_arg=_marker):
        filtered = []
        keys = self.actions.keys()
        keys.sort()
        for key in keys:
            action = self.actions[key]
            if object_id != _marker and not action.getObjectId() == object_id:
                continue
            if status and not action.getStatus() == status:
                continue
            if context_type != _marker and not action.getContextType() == context_type:
                continue
            if button != _marker and not action.getButton() == button:
                continue
            if action_type != _marker and not action.getActionType() == action_type:
                continue
            if action_arg != _marker and not action.getActionArg() == action_arg:
                continue
            filtered.append(action)
        return filtered

InitializeClass(FormActionContainer)