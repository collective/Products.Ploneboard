from Globals import package_home
from OFS.ObjectManager import BadRequestException
from Products.Archetypes import listTypes
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
from Products.CMFMember.Extensions.SimpleWorkflow \
    import setupWorkflow as setupSimpleWorkflow

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

# Install methods

def installDependencies(self, out):
    qi=getToolByName(self, 'portal_quickinstaller')
    qi.installProduct('PortalTransforms',)
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

    # clear the workflow for migration tool
    getToolByName(self, 'portal_workflow').setChainForPortalTypes('ControlTool', '')
    # set smart title after setup
    cm = self.cmfmember_control
    if cm.needUpgrading():
        cm.setTitle('CMFMember needs migration')
    else:
        cm.setTitle('CMFMember up to date')
    
def installMember(self, out):
    types = listTypes(CMFMember.PKG_NAME)

    # Member uses a special catalog 
    self.manage_addProduct['ZCatalog'].manage_addZCatalog(id='member_catalog', title='Members Only: CMFMember Catalog')
    self.member_catalog.addIndex(name='review_state', type='FieldIndex')
    
    installTypes(self, out,
                 types,
                 CMFMember.PKG_NAME)

    # Register member_catalog with archetype_tool
    at = getToolByName(self, 'archetype_tool')
    at.setCatalogsByType('Member', ['member_catalog', 'uid_catalog'])
    
    wf_tool = getToolByName(self, 'portal_workflow')
    wf_tool.setChainForPortalTypes((TYPE_NAME,), 'member_auto_workflow')
    wf_tool.updateRoleMappings()
    
    # register with portal factory
    site_props = self.portal_properties.site_properties
    if not hasattr(site_props,'portal_factory_types'):
        site_props._setProperty('portal_factory_types',('Member',), 'lines')

    
    
    

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

    
    setupWorkflow(self, out)
    setupSimpleWorkflow(self, out)

    print >> out, 'Successfully installed %s' % CMFMember.PKG_NAME
    import sys
    sys.stdout.write(out.getvalue())
    
    return out.getvalue()
