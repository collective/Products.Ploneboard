from BaseFormAction import BaseFormAction, registerFormAction
import TraverseTo

def factory(arg):
    """Create a new traverse-to-action action"""
    return TraverseToAction(arg)


class TraverseToAction(BaseFormAction):

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
                    action_url = actiondict['url'].strip()
                    if action_url.startswith('http://'):
                        action_url = action_url[7:]
                        action_url = action_url[action_url.index('/'):]
                    action_url = 'string:' + action_url
                    break
        if not action_url:
            raise ValueError, 'No %s action found for %s' % (action, controller_state.getContext().getId())
        return TraverseTo.TraverseTo(action_url)(controller_state)

registerFormAction('traverse_to_action', 
                   factory, 
                   'Traverse to the action specified in the argument (a TALES expression) for the current context object (e.g. string:view)')
