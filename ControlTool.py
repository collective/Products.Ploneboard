"""
$Id: ControlTool.py,v 1.6 2004/04/19 10:55:44 k_vertigo Exp $
"""
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, DevelopmentMode
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.Archetypes.utils import findDict
from Products.Archetypes.public import *
from Products.Archetypes.Schema import FieldList
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore import CMFCorePermissions

from Products.CMFMember.MemberDataContainer import getMemberFactory
import Products.CMFMember as CMFMember

import zLOG
import traceback
import sys
import types

def log(message,summary='',severity=0):
    zLOG.LOG('CMFMember: ', severity, summary, message)

def modify_fti(fti, allowed = ()):
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ''
    refs = findDict(fti['actions'], 'id', 'references')
    refs['visible'] = 0
    refs = findDict(fti['actions'], 'id', 'view')
    refs['name'] = 'Overview'
    refs['action'] = 'string:prefs_cmfmember_migration_overview'
    refs = findDict(fti['actions'], 'id', 'edit')
    refs['visible'] = 0
    refs = findDict(fti['actions'], 'id', 'metadata')
    refs['visible'] = 0
    
_upgradePaths = {}
_memberPaths = {}
_widgetRegistry = {}
control_id = 'cmfmember_control'
configlets = [ {'id':'cmfmember',
     'appId':'CMFMember',
     'name':'CMFMember control',
     'action':'string:${portal_url}/' + control_id + '/prefs_cmfmember_migration',
     'category':'Products',
     'permission': ManagePortal,
     'imageUrl':'group.gif'},]



# groups for our setup configlets
group = 'cmfmember|CMFMember|CMFMember setup'

class ControlTool( UniqueObject, BaseBTreeFolder):
    """Handles migrations between CMFMember releases"""

    id = control_id
    archetype_name = portal_type = meta_type = 'ControlTool'

    _needRecatalog = 0
    _needUpdateRole = 0

    global_allow = 0
    
    actions = (
        { 'id'            : 'migrations',
          'name'          : 'Migrations',
          'action'        : 'string:prefs_cmfmember_migration',
          'permissions'   : (CMFCorePermissions.ManageProperties,),
          'category'      : 'object',
        },
        { 'id'            : 'setup',
          'name'          : 'Setups',
          'action'        : 'string:prefs_cmfmember_setup',
          'permissions'   : (CMFCorePermissions.ManageProperties,),
          'category'      : 'object',
        },)

    manage_options = (
        { 'label' : 'Overview', 'action' : 'manage_overview' },
        { 'label' : 'Migrate', 'action' : 'manage_migrate' },
        { 'label' : 'Setup', 'action' : 'manage_setup' }, ) + ActionProviderBase.manage_options


    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_overview')
    security.declareProtected(ManagePortal, 'manage_migrate')

    manage_migrate = PageTemplateFile('skins/cmfmember_ctrl/prefs_cmfmember_migration.pt', globals())
    manage_overview = PageTemplateFile('skins/cmfmember_ctrl/prefs_cmfmember_migration_overview.pt', globals())

    version = ''
    
    def __init__(self, oid = None):
        if not oid: oid = self.id
        BaseBTreeFolder.__init__(self, oid)
        try:
            self.setSchemaCollector('type')
        except :
            pass
        
    # Add a visual note
    def om_icons(self):
        icons = ({
                    'path':'misc_/CMFPlone/tool.gif',
                    'alt':self.meta_type,
                    'title':self.meta_type,
                 },)
        if self.needUpgrading() \
           or self.needUpdateRole() \
           or self.needRecatalog():
            icons = icons + ({
                     'path':'misc_/PageTemplates/exclamation.gif',
                     'alt':'Error',
                     'title':'This Plone instance needs updating'
                  },)

        return icons

    ##############################################################
    # Public methods
    #
    # versions methods

    
    security.declareProtected(ManagePortal, 'getLog')
    def getLog(self):
        return getattr(self, '_log', None) 
    
    security.declareProtected(ManagePortal, 'getInstanceVersion')
    def getInstanceVersion(self):
        """ The version of installed CMFMember """
        # when we support more then one memberdata folder this check may 
        # have to be changed since different memberdata folders could be
        # different versions but shouldn't :)
        if getattr(self, 'version', '') == '':
            memberdata_tool = self.portal_memberdata
            if hasattr(memberdata_tool.__class__, 'portal_type') \
               and (memberdata_tool.__class__.portal_type == 'CMFMember Tool' \
               or memberdata_tool.__class__.portal_type == 'MemberDataContainer'):
                if hasattr(self.portal_memberdata,'getVersion'):
                    self.version = self.portal_memberdata.getVersion()
                else:
                    self.version = 'development'
            else:
                self.version = 'plone'
        return self.version.lower()

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of plone is on """
        self.version = version

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version ids, except current one """
        return _upgradePaths.keys()

    def knowMemberMigrations(self):
        """ All known member migrations """
        return _memberPaths
        

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFMember.version.lower()

    security.declareProtected(ManagePortal, 'getMemberTypesFileSystemVersion')
    def getMemberTypesFileSystemVersion(self):
        """ The version this instance of plone is on """
        portal = getToolByName(self, 'portal_url')
        memberdata_tool = portal.portal_memberdata
        vars = {}
        tempFolder = PortalFolder('temp').__of__(self)
        # don't store tempFolder in the catalog
        tempFolder.unindexObject()

        # get information form old MemberDataTool
        if hasattr(memberdata_tool.__class__, 'portal_type') \
           and memberdata_tool.__class__.portal_type == 'CMFMember Tool':
            member_type = memberdata_tool.typeName
            getMemberFactory(tempFolder, member_type)(member_type)
            memberInstance = getattr(tempFolder,member_type)
            getattr(tempFolder,member_type).unindexObject()
            # don't store memberInstance in the catalog
            vars[member_type] = memberInstance.version.lower()
            memberInstance.unindexObject()
        elif memberdata_tool.__class__ == CMFMember.MemberDataContainer.MemberDataContainer:
            for member_type in memberdata_tool.getAllowedMemberTypes():
                getMemberFactory(tempFolder, member_type)(member_type)
                memberInstance = getattr(tempFolder,member_type)
                getattr(tempFolder,member_type).unindexObject()
                # don't store memberInstance in the catalog
                vars[member_type] = memberInstance.version.lower()
                memberInstance.unindexObject() 
        return vars.items()
    
    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        need = self.getInstanceVersion() != self.getFileSystemVersion()
        if need:
            self.setTitle('CMFMember not up to date')
        else:
            self.setTitle('CMFMember up to date')
        return need



    security.declareProtected(ManagePortal, 'coreVersions')
    def coreVersions(self):
        """ Useful core information """
        vars = {}
        cp = self.Control_Panel
        vars['CMFMember Instance'] = self.getInstanceVersion()
        vars['CMFMember File System'] = self.getFileSystemVersion()
            
        return vars

    security.declareProtected(ManagePortal, 'coreVersionsList')
    def coreVersionsList(self):
        """ Useful core information """
        res = self.coreVersions().items()
        res.sort()
        return res

    security.declareProtected(ManagePortal, 'needUpdateRole')
    def needUpdateRole(self):
        """ Do roles need to be updated? """
        return self._needUpdateRole

    security.declareProtected(ManagePortal, 'needRecatalog')
    def needRecatalog(self):
        """ Does this thing now need recataloging? """
        return self._needRecatalog

    ##############################################################
    # the setup widget registry
    # this is a whole bunch of wrappers
    # Really an unprotected sub object
    # declaration could do this...

    def _getWidget(self, widget):
        """ We cant instantiate widgets at run time
        but can send all get calls through here... """
        _widget = _widgetRegistry[widget]
        obj = getToolByName(self, 'portal_url').getPortalObject()
        return _widget(obj)

    security.declareProtected(ManagePortal, 'listWidgets')
    def listWidgets(self):
        """ List all the widgets """
        return _widgetRegistry.keys()

    security.declareProtected(ManagePortal, 'getDescription')
    def getDescription(self, widget):
        """ List all the widgets """
        return self._getWidget(widget).description

    security.declareProtected(ManagePortal, 'listAvailable')
    def listAvailable(self, widget):
        """  List all the Available things """
        return self._getWidget(widget).available()

    security.declareProtected(ManagePortal, 'listInstalled')
    def listInstalled(self, widget):
        """  List all the installed things """
        return self._getWidget(widget).installed()

    security.declareProtected(ManagePortal, 'listNotInstalled')
    def listNotInstalled(self, widget):
        """ List all the not installed things """
        avail = self.listAvailable(widget)
        install = self.listInstalled(widget)
        return [ item for item in avail if item not in install ]

    security.declareProtected(ManagePortal, 'activeWidget')
    def activeWidget(self, widget):
        """ Show the state """
        return self._getWidget(widget).active()

    security.declareProtected(ManagePortal, 'setupWidget')
    def setupWidget(self, widget):
        """ Show the state """
        return self._getWidget(widget).setup()

    security.declareProtected(ManagePortal, 'runWidget')
    def runWidget(self, widget, item, **kwargs):
        """ Run the widget """
        return self._getWidget(widget).run(item, **kwargs)

    security.declareProtected(ManagePortal, 'installItems')
    def installItems(self, widget, items):
        """ Install the items """
        return self._getWidget(widget).addItems(items)

    ##############################################################

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=1):
        """ perform the upgrade """

        get_transaction().commit(1)

        # keep it simple
        out = []

        self._check()
        
        if dry_run:
            out.append(("Dry run selected.", zLOG.INFO))

        newv = REQUEST.get('force_instance_version', self.getInstanceVersion())

        out.append(("Starting the migration from "
                    "version: %s" % newv, zLOG.INFO))

        while newv is not None:
            out.append(("Attempting to upgrade from: %s" % newv, zLOG.INFO))
            # commit work in progress between each version
            get_transaction().commit(1)
            # if we modify the portal root and commit a sub transaction
            # the skin data will disappear, explicitly set it up on each
            # subtrans, the alternative is to traverse again to the root on
            # after each which will trigger the normal implicit skin setup.
            aq_parent( aq_inner( self ) ).setupCurrentSkin()
            try:
                newv, msgs = self._upgrade(newv)
                if msgs:
                    for msg in msgs:
                        # if string make list
                        if type(msg) == type(''):
                            msg = [msg,]
                        # if no status, add one
                        if len(msg) == 1:
                            msg.append(zLOG.INFO)
                        out.append(msg)
                if newv is not None:
                    out.append(("Upgrade to: %s, completed" % newv, zLOG.INFO))
                    self.setInstanceVersion(newv)

            except:
                out.append(("Upgrade aborted", zLOG.ERROR))
                out.append(("Error type: %s" % sys.exc_type, zLOG.ERROR))
                out.append(("Error value: %s" % sys.exc_value, zLOG.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, zLOG.ERROR))

                # set newv to None
                # to break the loop
                newv = None
                if swallow_errors:
                    # abort transaction to safe the zodb
                    get_transaction().abort(1)
                else:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        out.append(("End of upgrade path, migration has finished", zLOG.INFO))

        if self.needUpgrading():
            out.append((("The upgrade path did NOT reach "
                        "current version"), zLOG.PROBLEM))
            out.append(("Migration has failed", zLOG.PROBLEM))
        else:
            out.append((("Your ZODB and Filesystem Plone "
                         "instances are now up-to-date."), zLOG.INFO))

        # do this once all the changes have been done
        if self.needRecatalog():
            try:
                self.portal_catalog.refreshCatalog()
                self._needRecatalog = 0
            except:
                out.append(("Exception was thrown while cataloging",
                            zLOG.ERROR))
                out += traceback.format_tb(sys.exc_traceback)
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if self.needUpdateRole():
            try:
                self.portal_workflow.updateRoleMappings()
                self._needUpdateRole = 0
            except:
                out.append((("Exception was thrown while updating "
                             "role mappings"), zLOG.ERROR))
                out += traceback.format_tb(sys.exc_traceback)
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if dry_run:
            out.append(("Dry run selected, transaction aborted", zLOG.INFO))
            # abort all work done in this transaction, this roles back work
            # done in previous sub transactions
            get_transaction().abort()

        # log all this to the ZLOG
        for msg, sev in out:
            log(msg, severity=sev)

        self._log = out

        if REQUEST :
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

        return 'Migrated...'

    def getConfiglets(self):
        return tuple(configlets)
    ##############################################################
    # Private methods

    def _check(self):
        """ Are we inside a Plone site?  Are we allowed? """
        if not hasattr(self,'portal_url'):
            raise 'You must be in a Plone site to migrate.'

    def _upgrade(self, version):
        version = version.lower()
        if not _upgradePaths.has_key(version):
            return None, ("No upgrade path found from %s" % version,)

        newversion, function = _upgradePaths[version]
        res = function(self.aq_parent)
        return newversion, res

def registerUpgradePath(oldversion, newversion, function, type = 'Member'):
    """ Basic register func """
    if type != 'Memmber':
        _upgradePaths[oldversion.lower()] = [newversion.lower(), function]
    else:
        _memberPaths[oldversion.lower()] = [newversion.lower(), function]

def registerSetupWidget(widget):
    """ Basic register things """
    for wc in widget.configlets:
        configlets.append(wc)
    _widgetRegistry[widget.type] = widget

registerType(ControlTool, 'CMFMember')
InitializeClass(ControlTool)
