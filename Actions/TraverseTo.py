from BaseFormAction import BaseFormAction, registerFormAction
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply

def factory(arg):
    """Create a new traverse-to action"""
    return TraverseTo(arg)


class TraverseTo(BaseFormAction):
    def __call__(self, controller_state):
        url = self.getArg(controller_state)
        REQUEST = controller_state.getContext().REQUEST
        for (key, value) in controller_state.kwargs.items():
            REQUEST.set(key, value)
        # make sure target exists
        context = controller_state.getContext()
        obj = context.restrictedTraverse(url, default=None)
        if obj is None:
            raise ValueError, 'Unable to find %s\n' % str(url)
        return mapply(obj, REQUEST.args, REQUEST,
                               call_object, 1, missing_name, dont_publish_class,
                               REQUEST, bind=1)


registerFormAction('traverse_to', 
                   factory, 
                   'Traverse to the URL specified in the argument (a TALES expression).  The URL can either be absolute or relative.')