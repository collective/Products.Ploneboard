from AccessControl import Role, ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFFormController.FormController import registerFormAction
from Products.CMFFormController.utils import log
from IFormAction import IFormAction

# ###########################################################################
class BaseFormAction(Role.RoleManager):
    __implements__ = IFormAction,

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess('allow')

    expression = None

    def __init__(self, arg=None):
        if arg is None:
            log('No argument specified for action.  This means that some of your CMFFormController actions may have been corrupted.  You may be able to fix them by editing the actions in question via the Actions tab and re-saving them.')
        else:
            self.expression = Expression(arg)


    def __call__(self, controller_state):
        raise NotImplementedError


    def getArg(self, controller_state):
        """Generate an expression context for the TALES expression used as
        the argument to the action and evaluate the expression."""
        context = controller_state.getContext()

        portal = getToolByName(context, 'portal_url').getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        
        if context is None or not hasattr(context, 'aq_base'):
            folder = portal
        else:
            folder = context
            # Search up the containment hierarchy until we find an
            # object that claims to be a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))

        object_url = context.absolute_url()

        if portal_membership.isAnonymousUser():
            member = None
        else:
            member = portal_membership.getAuthenticatedMember()
        data = {
            'object_url':   object_url,
            'folder_url':   folder.absolute_url(),
            'portal_url':   portal.absolute_url(),
            'object':       context,
            'folder':       folder,
            'portal':       portal,
            'nothing':      None,
            'request':      getattr( context, 'REQUEST', None ),
            'modules':      SecureModuleImporter,
            'member':       member,
            'state':        controller_state,
            }
        exprContext = getEngine().getContext(data)
        return self.expression(exprContext)


    def updateQuery(self, url, kwargs):
        """Utility method that takes a URL, parses its existing query string,
        url encodes 
        and updates the query string using the values in kwargs"""
        import urlparse 
        import urllib 
        import cgi

        # parse the existing URL
        parsed_url = list(urlparse.urlparse(url))
        # get the existing query string
        qs = parsed_url[4]
        # parse the query into a dict
        d = cgi.parse_qs(qs, 1)
        # XXX not sure if this is the right way to handle this
        # parse_qs appears to return values in lists -- we concatenate them 
        # with commas and combine into a single string
        dict = {}
        for (k,v) in d.items():
            dict[k] = ','.join(v)
        # update the dict
        dict.update(kwargs)
        # re-encode the string
        parsed_url[4] = urllib.urlencode(dict)
        # rebuild the URL
        return urlparse.urlunparse(parsed_url)
        
    
# ###########################################################################