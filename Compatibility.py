"""
Provides for code compatiblity between silva and the cmf.

Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Acquisition import aq_get
from OFS.ObjectManager import UNIQUE
from Interface import Interface
from ExtensionClass import Base

import Configuration
from Exceptions import CompatibilityException

#################################
### Interface declarations/assertions
if Configuration.UsingCMF:
    from Products.CMFCore.interfaces import portal_actions, portal_metadata
    IActionProvider = portal_actions.ActionProvider
    IPortalMetadata = portal_metadata.portal_metadata
else:
    class IActionProvider(Interface): pass
    class IPortalMetadata(Interface): pass

#################################
### Action Provider and Info
if Configuration.UsingCMF:
    from Products.CMFCore.ActionInformation import ActionInformation
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
else:
    ActionInformation = None

    class ActionProviderBase(Base):
        pass

def actionFactory(**kw):
    if ActionInformation is None:
        return None
    return ActionInformation(**kw)

#################################
### Service Lookup

if Configuration.UsingCMF:
    from Products.CMFCore.utils import getToolByName

else:
    _marker = []

    SilvaToolMap = {
        'portal_catalog':'service_catalog',
        'portal_annotations':'service_annotations',
        'portal_metadata':'service_metadata'
        }

    def getToolByName(ctx, service_name, default=_marker):
        try:
            silva_name = SilvaToolMap[service_name]
        except KeyError, e:
            raise CompatibilityException(str(e))

        try:
            tool = aq_get(ctx, silva_name, default, 1)
        except AttributeError:
            if default is _marker:
                raise
            return default

        if tool is _marker:
            raise AttributeError(silva_name)

        return tool

#################################
### Content Type Lookup
if Configuration.UsingCMF:
    def getContentTypeNames(ctx):
        pt = getToolByName(ctx, 'portal_types')
        return pt.objectIds()
else:
    _allowed_content_types = []

    def registerTypeForMetadata(type_name):
        if type_name not in _allowed_content_types:
            _allowed_content_types.append(type_name)

    def getContentTypeNames(ctx):
        return tuple(_allowed_content_types)
        #return ctx.get_silva_addables_all()

if Configuration.UsingCMF:
    def getContentType(content):
        return content.getPortalTypeName()

else:
    def getContentType(content):
        return content.meta_type

#################################
### Permissions
# only set if not overridden by user/developer
if Configuration.UsingCMF:
    from Products.CMFCore import CMFCorePermissions
    if Configuration.pMetadataView is None:
        Configuration.pMetadataView = CMFCorePermissions.View
    if Configuration.pMetadataEdit is None:
        Configuration.pMetadataEdit = CMFCorePermissions.ModifyPortalContent
    if Configuration.pMetadataManage is None:
        Configuration.pMetadataManage = CMFCorePermissions.ManagePortal
else:
    from Products.Silva import SilvaPermissions
    if Configuration.pMetadataView is None:
        Configuration.pMetadataView = SilvaPermissions.View
    if Configuration.pMetadataEdit is None:
        Configuration.pMetadataEdit = SilvaPermissions.ChangeSilvaContent
    if Configuration.pMetadataManage is None:
        Configuration.pMetadataManage = SilvaPermissions.ViewManagementScreens

#################################
### Catalog Expressions for ProxyIndex
if Configuration.UsingCMF:
    tem = "python: object.portal_metadata.getMetdatata(object)['%s']['%s']"
    index_expression_template = tem
else:
    tem = "python: object.service_metadata.getMetadataValue(object, '%s', '%s')"
    index_expression_template = tem

#################################
### Misc
if Configuration.UsingCMF:
    from Products.CMFCore.utils import UniqueObject
else:
    class ImmutableId(Base):

        """ Base class for objects which cannot be renamed.
        """
        def _setId(self, id):

            """ Never allow renaming!
            """
            if id != self.getId():
                raise MessageDialog(
                    title='Invalid Id',
                    message='Cannot change the id of this object',
                    action ='./manage_main',)

    class UniqueObject (ImmutableId):

        """ Base class for objects which cannot be "overridden" / shadowed.
        """
        __replaceable__ = UNIQUE

