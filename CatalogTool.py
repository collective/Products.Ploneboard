from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass
from ZODB.POSException import ConflictError

from Products.CMFCore.interfaces.portal_catalog \
        import portal_catalog as ICatalogTool
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.CMFPlone.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from Products.ZCatalog.ZCatalog import ZCatalog


class CatalogTool(BaseTool):
    """Override CatalogTool so we can add some extra methods to all objects
    before cataloging them."""
    __implements__ = (ICatalogTool, ActionProviderBase.__implements__)

    meta_type = 'Portal CMFMember Catalog Tool'
    security = ClassSecurityInfo()

    def catalog_object(self, object, uid, idxs=[]):
        try:
            usersWithLocalRoles = dict(object.get_local_roles()).keys()
        except ConflictError:
            raise
        except:
            usersWithLocalRoles = []

        try:
            owner_info = object.owner_info()
            owner = '/' + owner_info['path'] + '/' + owner_info['id']
        except ConflictError:
            raise
        except:
            owner = None

        wf = getattr(self, 'portal_workflow', None)
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}

        vars['indexedOwner'] = owner
        vars['indexedUsersWithLocalRoles'] = usersWithLocalRoles

        w = IndexableObjectWrapper(vars, object)

        ZCatalog.catalog_object(self, w, uid, idxs)


CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
