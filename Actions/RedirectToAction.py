from BaseFormAction import BaseFormAction, registerFormAction
import RedirectTo

def factory(arg):
    """Create a new redirect-to-action action"""
    return RedirectToAction(arg)


class RedirectToAction(BaseFormAction):

    def __call__(self, controller_state):
        action = self.getArg(controller_state)
        action_url = 'string:' + controller_state.getContext().getTypeInfo().getActionById(action)
        return RedirectTo.RedirectTo(action_url)(controller_state)

registerFormAction('redirect_to_action', 
                   factory, 
                   'Redirect to the action specified in the argument (a TALES expression) for the current context object (e.g. string:view)')