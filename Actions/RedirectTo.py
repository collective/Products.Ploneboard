from BaseFormAction import BaseFormAction, registerFormAction
from urlparse import urlparse, urljoin

def factory(arg):
    """Create a new redirect-to action"""
    return RedirectTo(arg)


class RedirectTo(BaseFormAction):
    def __call__(self, controller_state):
        url = self.getArg(controller_state)
        context = controller_state.getContext()
        # see if this is a relative url or an absolute
        if len(urlparse(url)[1]) == 0:
            # No host specified, so url is relative.  Get an absolute url.
            url = urljoin(context.absolute_url()+'/', url)
        url = self.updateQuery(url, controller_state.kwargs)
        return context.REQUEST.RESPONSE.redirect(url)


registerFormAction('redirect_to', 
                   factory, 
                   'Redirect to the URL specified in the argument (a TALES expression).  The URL can either be absolute or relative.')