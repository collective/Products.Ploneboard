from BaseFormAction import BaseFormAction, registerFormAction
import TraverseTo

def factory(arg):
    """Create a new traverse-to-action action"""
    return TraverseToAction(arg)


class TraverseToAction(BaseFormAction):

    def __call__(self, controller_state):
        action = self.getArg(controller_state)
        action_url = 'string:' + controller_state.getContext().getTypeInfo().getActionById(action)
        return TraverseTo.TraverseTo(action_url)(controller_state)

registerFormAction('traverse_to_action', 
                   factory, 
                   'Traverse to the action specified in the argument (a TALES expression) for the current context object (e.g. string:view)')