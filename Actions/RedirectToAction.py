from BaseFormAction import BaseFormAction, registerFormAction
import RedirectTo

def factory(arg):
    """Create a new redirect-to-action action"""
    return RedirectToAction(arg)


class RedirectToAction(BaseFormAction):

    def __call__(self, controller_state):
        action = self.getArg(controller_state)
        action_url = None
        try:
            action_url = 'string:' + controller_state.getContext().getTypeInfo().getActionById(action)
        except ValueError:
            actions = controller_state.getContext().portal_actions.listFilteredActionsFor(controller_state.getContext())
            # flatten the actions as we don't care where they are
            actions = reduce(lambda x,y,a=actions:  x+a[y], actions.keys(), [])
            for actiondict in actions:
                if actiondict['id'] == action:
                    action_url = 'string:' + actiondict['url'].strip()
                    break
        if not action_url:
            raise ValueError, 'No %s action found for %s' % (action, controller_state.getContext().getId())
        return RedirectTo.RedirectTo(action_url)(controller_state)

registerFormAction('redirect_to_action',
                   factory,
                   'Redirect to the action specified in the argument (a TALES expression) for the current context object (e.g. string:view)')
