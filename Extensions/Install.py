from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.PloneBannerManager.config import *
from Products.PloneBannerManager.BannerPermissions import *
from Products.PloneBannerManager.BannerWorkflow import BANNER_WORKFLOW_ID, \
    BANNER_WORKFLOW_TITLE

from StringIO import StringIO

def install_folder_tabs(self, out):
    """Make sure the BannerFolder type has folderish tabs"""

    portal_props = getToolByName(self, 'portal_properties')
    site_props = getattr(portal_props, 'site_properties', None)
    attrname = 'use_folder_tabs'
    if site_props is None:
        print >> out, "portal_properties.site_properties not found, cannot make BannerFolder folderish"
        return
    folderish_types = list(site_props.getProperty(attrname))
    if 'BannerFolder' not in folderish_types:
        folderish_types.append('BannerFolder')
        site_props._updateProperty(attrname, folderish_types)
        print >> out, "Added BannerFolder to the list of folderish types"

def install_workflow(self, out):
    wtool = self.portal_workflow

    try:
        wtool._addRole(ManageBanners)
        print >> out, "Added '%s' role to the list of roles" % ManageBanners
    except:
        print >> out, "Failed to add '%s' role. Maybe it already exists?" % ManageBanners

    if BANNER_WORKFLOW_ID not in wtool.objectIds():
        type = "%s (%s)" % (BANNER_WORKFLOW_ID, BANNER_WORKFLOW_TITLE)
        wtool.manage_addWorkflow(id=BANNER_WORKFLOW_ID, workflow_type=type)
        wtool.setChainForPortalTypes(('BannerImage',), BANNER_WORKFLOW_ID)
    
    # If BannerFolder doesn't have a workflow defined, use folder_workflow
    if wtool.getChainFor('BannerFolder') is None:
        wtool.setChainForPortalTypes(('BannerFolder',), 'folder_workflow')

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    install_folder_tabs(self, out)
    install_workflow(self, out)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
