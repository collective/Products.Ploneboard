from Globals import package_home
from OFS.ObjectManager import BadRequestException
from Products.Archetypes.public import listTypes
from Products.Archetypes.debug import log, log_exc
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName, minimalpath
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.Expression import Expression

from Products.CMFCore.utils import getToolByName, manage_addTool
from Products.CMFCore.DirectoryView import addDirectoryViews, \
     registerDirectory, manage_listAvailableDirectories
from Products.CMFCore.utils import getToolByName
from Products.CMFMember import ControlTool
from StringIO import StringIO
from os.path import isdir, join

import Products.CMFMember as CMFMember
from Products.CMFMember.Extensions.Workflow \
    import setupWorkflow, workflow_transfer

from Products.CMFMember.MemberCatalogTool import MemberCatalogTool

import sys, os, string

TYPE_NAME = 'Member'

def uninstallControlTool(portal, out):
    controltool = getToolByName(portal, 'portal_controlpanel')
    cm = getToolByName(portal, 'cmfmember_control')
    for configlet in cm.getConfiglets():
        controltool.unregisterConfiglet(configlet['id'])

def uninstall(self):
    out=StringIO()
    uninstallControlTool(self, out)
    #Remove user deletion override
    acl_users = getToolByName(self, 'acl_users')
    try:
        del acl_users.userFolderDelUsers
    except KeyError, AttributeError:
        pass

# Install methods

def installDependencies(self, out):
    qi=getToolByName(self, 'portal_quickinstaller')
    qi.installProduct('Archetypes')

def installControlTool(self, out):
    """
    Install a migration tool if there isn't any. We also set the version at install,
    this will indicate that we need some migration if the instance version of
    migration tool isn't the same as the one on filesystem.
    """
    if hasattr(self,'cmfmember_control'):
        self.manage_delObjects(['cmfmember_control'])

    m = self.manage_addProduct[CMFMember.PKG_NAME]
    manage_addTool(m, 'ControlTool')

    # XXX: the class name is used as tool name when Archetype, don't know how to change it.
    cp = getToolByName(self, 'portal_controlpanel')
    cm = getToolByName(self, 'cmfmember_control')
    # we add our groups to the controlpanel tool, groups are used to display configlets
    # in the setup tab of our migration tool.
    if 'cmfmember' not in cp.getGroupIds(): cp.groups.append(ControlTool.group)

    # remove any old existing configlets
    for configlet in cm.getConfiglets():
        cp.unregisterConfiglet(configlet['id'])
    # add configlet to the plone control panel
    cp.registerConfiglets(cm.getConfiglets())

    # set smart title after setup
    cm = self.cmfmember_control
    if cm.needUpgrading():
        cm.setTitle('CMFMember needs migration')
    else:
        cm.setTitle('CMFMember up to date')

    nl_meta_types = self.portal_properties.navtree_properties.metaTypesNotToList
    nl_meta_types = list(nl_meta_types)
    try:
        nl_meta_types.index('ControlTool')
    except ValueError:
        nl_meta_types.append('ControlTool')
    self.portal_properties.navtree_properties.metaTypesNotToList = tuple( nl_meta_types )


def installMember(self, out):
    types = listTypes(CMFMember.PKG_NAME)

    class args:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    # Member uses a special catalog tool
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if not 'member_catalog' in portal.objectIds():
        m = self.manage_addProduct[CMFMember.PKG_NAME]
        m.manage_addTool(MemberCatalogTool.meta_type)
        mcat = getToolByName(self, 'member_catalog')

    installTypes(self, out,
                 types,
                 CMFMember.PKG_NAME)

    # Register member_catalog with archetype_tool
    at = getToolByName(self, 'archetype_tool')
    at.setCatalogsByType('Member', ['member_catalog', 'portal_catalog'])

    # register with portal factory
    site_props = self.portal_properties.site_properties
    if not hasattr(site_props,'portal_factory_types'):
        site_props._setProperty('portal_factory_types',('Member',), 'lines')

    # add a form_controller action so that preference edit traverses back
    # to the preferences panel
    fc = getToolByName(self, 'portal_form_controller')
    fc.addFormAction('validate_integrity',   # template/script
                     'success',              # status
                     'Member',               # context
                     None,                   # button
                     'traverse_to_action',   # action
                     'string:edit')          # argument

def installSkins(self, out):
    # we do this by hand since we don't want all of our skins to be
    # added to the skin path yet
    skinsTool = getToolByName(self, 'portal_skins')
    skins = ['cmfmember', 'cmfmember_ctrl']
    earlySkins = ['cmfmember_ctrl']
    for skin in skins:
        if hasattr(skinsTool, skin):
            # delete old skin path i.e (If we use OldCMFMember in testcases)
            skinsTool.manage_delObjects([skin])
    product_skins_dir = 'skins'
    globals = CMFMember.GLOBALS
    fullProductSkinsPath = join(package_home(globals), product_skins_dir)
    productSkinsPath = minimalpath(fullProductSkinsPath)
    registered_directories = manage_listAvailableDirectories()
    if productSkinsPath not in registered_directories:
        registerDirectory(product_skins_dir, globals)
    try:
        addDirectoryViews(skinsTool, product_skins_dir, globals)
    except BadRequestException, e:
        pass  # directory view has already been added

    files = os.listdir(fullProductSkinsPath)
    #import pdb; pdb.set_trace()
    for productSkinName in files:
        if (isdir(join(fullProductSkinsPath, productSkinName))
            and productSkinName != 'CVS'
            and productSkinName != '.svn'
            and productSkinName in earlySkins):
            for skinName in skinsTool.getSkinSelections():
                path = skinsTool.getSkinPath(skinName)
                path = [i.strip() for i in  path.split(',')]
                try:
                    if productSkinName not in path:
                        path.insert(path.index('custom') +1, productSkinName)
                except ValueError:
                    if productSkinName not in path:
                        path.append(productSkinName)
                path = ','.join(path)
                skinsTool.addSkinSelection(skinName, path)

def install(self):
    out=StringIO()

    # only installs here, all tool replacing is done in migration
    installDependencies(self, out)
    installControlTool(self, out)
    installSkins(self, out)
    installMember(self, out)

    # We need to do the updateRoleMappings only once after all workflows have been set
    # because otherwise the empty one(i.e ControlTool) are reseted to (Default)
    # clear the workflow for migration tool
    wf_tool = getToolByName(self, 'portal_workflow')
    wf_tool.setChainForPortalTypes((TYPE_NAME,), 'member_auto_workflow')
    wf_tool.setChainForPortalTypes(('ControlTool',), '')
    wf_tool.updateRoleMappings()

    setupWorkflow(self, out)

    return out.getvalue()
