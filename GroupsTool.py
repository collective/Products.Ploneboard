##############################################################################
#
# Copyright (c) 2003 Connexions Projects and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic usergroup tool.

$Id: GroupsTool.py,v 1.34 2004/11/16 12:03:59 pjgrizel Exp $
"""

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from GroupsToolPermissions import AddGroups
from GroupsToolPermissions import ManageGroups
from GroupsToolPermissions import DeleteGroups
from GroupsToolPermissions import ViewGroups
from GroupsToolPermissions import SetGroupOwnership
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from interfaces.portal_groups import portal_groups as IGroupsTool
from global_symbols import *

# Optional feature-preview support
import PloneFeaturePreview


class GroupsTool (UniqueObject, SimpleItem, ActionProviderBase, ):
    """ This tool accesses group data through a GRUF acl_users object.

    It can be replaced with something that groups member data in a
    different way.
    """
    # Show implementation only if  IGroupsTool is defined
    # The latter will work only with Plone 1.1 => hence, the if
    if hasattr(ActionProviderBase, '__implements__'):
        __implements__ = (IGroupsTool, ActionProviderBase.__implements__)

    id = 'portal_groups'
    meta_type = 'CMF Groups Tool'
    _actions = ()

    security = ClassSecurityInfo()

    groupworkspaces_id = "groups"
    groupworkspaces_title = "Groups"
    groupWorkspacesCreationFlag = 1
    groupWorkspaceType = "Folder"
    groupWorkspaceContainerType = "Folder"

    manage_options=(
            ( { 'label' : 'Configure'
                     , 'action' : 'manage_config'
                    },
                ) + ActionProviderBase.manage_options +
                ( { 'label' : 'Overview'
                     , 'action' : 'manage_overview'
                     },
                ) + SimpleItem.manage_options)

    #                                                   #
    #                   ZMI methods                     #
    #                                                   #
    security.declareProtected(ViewManagementScreens, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainGroupsTool', globals())     # unlike MembershipTool
    security.declareProtected(ViewManagementScreens, 'manage_config')
    manage_config = DTMLFile('dtml/configureGroupsTool', globals())

    security.declareProtected(ManagePortal, 'manage_setGroupWorkspacesFolder')
    def manage_setGroupWorkspacesFolder(self, id='groups', title='Groups', REQUEST=None):
        """ZMI method for workspace container name set."""
        self.setGroupWorkspacesFolder(id, title)
        return self.manage_config(manage_tabs_message="Workspaces folder name set to %s" % id)

    security.declareProtected(ManagePortal, 'manage_setGroupWorkspaceType')
    def manage_setGroupWorkspaceType(self, type='Folder', REQUEST=None):
        """ZMI method for workspace type set."""
        self.setGroupWorkspaceType(type)
        return self.manage_config(manage_tabs_message="Group Workspaces type set to %s" % type)

    security.declareProtected(ManagePortal, 'manage_setGroupWorkspaceContainerType')
    def manage_setGroupWorkspaceContainerType(self, type='Folder', REQUEST=None):
        """ZMI method for workspace type set."""
        self.setGroupWorkspaceContainerType(type)
        return self.manage_config(manage_tabs_message="Group Workspaces container type set to %s" % type)

    security.declareProtected(ViewGroups, 'getGroupById')
    def getGroupById(self, id):
        """
        Returns the portal_groupdata-ish object for a group corresponding to this id.
        """
        if id==None:
            return None
        g = self.acl_users.getGroupByName(id, None)
        if g is not None:
            g = self.wrapGroup(g)
        return g

    security.declareProtected(ViewGroups, 'getGroupsByUserId')
    def getGroupsByUserId(self, userid):
        """Returns a list of the groups the user corresponding to 'userid' belongs to."""
        #log("getGroupsByUserId(%s)" % userid)
        user = self.acl_users.getUser(userid)
        #log("user '%s' is in groups %s" % (userid, user.getGroups()))
        if user:
            groups = user.getGroups() or []
        else:
            groups = []
        return [self.getGroupById(elt) for elt in groups]

    security.declareProtected(ViewGroups, 'listGroups')
    def listGroups(self):
        """Returns a list of the available portal_groupdata-ish objects."""
        return [self.wrapGroup(elt) for elt in self.acl_users.getGroups()]

    security.declareProtected(ViewGroups, 'listGroupIds')
    def listGroupIds(self):
        """Returns a list of the available groups' ids as entered (without group prefixes)."""
        return self.acl_users.getGroupNames()

    security.declareProtected(ViewGroups, 'listGroupNames')
    def listGroupNames(self):
        """Returns a list of the available groups' ids as entered (without group prefixes)."""
        return self.acl_users.getGroupNames()

    security.declarePublic("isGroup")
    def isGroup(self, u):
        """Test if a user/group object is a group or not.
        You must pass an object you get earlier with wrapUser() or wrapGroup()
        """
        base = aq_base(u)
        if hasattr(base, "isGroup") and base.isGroup():
            return 1
        return 0

##    security.declarePrivate('getPureUserNames')
##    def getPureUserNames(self):
##        """Get the usernames (ids) of only users. """
##        return self.acl_users.getPureUserNames()

##    security.declarePrivate('getPureUsers')
##    def getPureUsers(self):
##        """Get the actual (unwrapped) user objects of only users. """
##        return self.acl_users.getPureUsers()

    security.declareProtected(View, 'searchForGroups')
    def searchForGroups(self, REQUEST = {}, **kw):
        """Return a list of groups meeting certain conditions. """
        # arguments need to be better refined?
        if REQUEST:
            dict = REQUEST
        else:
            dict = kw

        name = dict.get('name', None)
        email = dict.get('email', None)
        roles = dict.get('roles', None)
        title = dict.get('title', None)
        last_login_time = dict.get('last_login_time', None)
        #is_manager = self.checkPermission('Manage portal', self)

        if name:
            name = name.strip().lower()
        if not name:
            name = None
        if email:
            email = email.strip().lower()
        if not email:
            email = None
        if title:
            title = title.strip().lower()
        if not title:
            title = None

        res = []
        portal = self.portal_url.getPortalObject()
        for g in portal.portal_groups.listGroups():
            #if not (g.listed or is_manager):
            #    continue
            if name:
                if (g.getGroupName().lower().find(name) == -1) and (g.getGroupId().lower().find(name) == -1):
                    continue
            if email:
                if g.email.lower().find(email) == -1:
                    continue
            if roles:
                group_roles = g.getRoles()
                found = 0
                for r in roles:
                    if r in group_roles:
                        found = 1
                        break
                if not found:
                    continue
            if title:
                if g.title.lower().find(title) == -1:
                    continue
            if last_login_time:
                if g.last_login_time < last_login_time:
                    continue
            res.append(g)

        return res

    security.declareProtected(AddGroups, 'addGroup')
    def addGroup(self, id, roles = [], groups = [], *args, **kw):
        """Create a group, and a group workspace if the toggle is on, with the supplied id, roles, and domains.

        Underlying user folder must support adding users via the usual Zope API.
        Passwords for groups ARE irrelevant in GRUF."""
        if id in self.listGroupIds():
            raise ValueError, "Group '%s' already exists." % (id, )
        self.acl_users.userFolderAddGroup(id, roles = roles, groups = groups )
        self.createGrouparea(id)
        self.getGroupById(id).setProperties(**kw)

    security.declareProtected(ManageGroups, 'editGroup')
    def editGroup(self, id, roles = None, groups = None, *args, **kw):
        """Edit the given group with the supplied password, roles, and domains.

        Underlying user folder must support editing users via the usual Zope API.
        Passwords for groups seem to be currently irrelevant in GRUF."""
        self.acl_users.userFolderEditGroup(id, roles = roles, groups = groups, )
        self.getGroupById(id).setProperties(**kw)

    security.declareProtected(DeleteGroups, 'removeGroups')
    def removeGroups(self, ids, keep_workspaces=0):
        """Remove the group in the provided list (if possible).

        Will by default remove this group's GroupWorkspace if it exists. You may
        turn this off by specifying keep_workspaces=true.
        Underlying user folder must support removing users via the usual Zope API."""
        for gid in ids:
            gdata = self.getGroupById(gid)
            gusers = gdata.getGroupMembers()
            for guser in gusers:
                gdata.removeMember(guser.id)

        self.acl_users.userFolderDelGroups(ids)
        gwf = self.getGroupWorkspacesFolder()
        if not gwf: # _robert_
            return
        if not keep_workspaces:
            for id in ids:
                if hasattr(aq_base(gwf), id):
                    gwf._delObject(id)

    security.declareProtected(SetGroupOwnership, 'setGroupOwnership')
    def setGroupOwnership(self, group, object):
        """Make the object 'object' owned by group 'group' (a portal_groupdata-ish object).

        For GRUF this is easy. Others may have to re-implement."""
        user = group.getGroup()
        if user is None:
            raise ValueError, "Invalid group: '%s'." % (group, )
        object.changeOwnership(user)
        object.manage_setLocalRoles(user.getId(), ['Owner'])

    security.declareProtected(ManagePortal, 'setGroupWorkspacesFolder')
    def setGroupWorkspacesFolder(self, id="", title=""):
        """ Set the location of the Group Workspaces folder by id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders.

         If anyone really cares, we can probably make the id work as a path as well,
         but for the moment it's only an id for a folder in the portal root, just like the
         corresponding MembershipTool functionality. """
        self.groupworkspaces_id = id.strip()
        self.groupworkspaces_title = title

    security.declareProtected(ManagePortal, 'getGroupWorkspacesFolderId')
    def getGroupWorkspacesFolderId(self):
        """ Get the Group Workspaces folder object's id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """
        return self.groupworkspaces_id

    security.declareProtected(ManagePortal, 'getGroupWorkspacesFolderTitle')
    def getGroupWorkspacesFolderTitle(self):
        """ Get the Group Workspaces folder object's title.
        """
        return self.groupworkspaces_title

    security.declarePublic('getGroupWorkspacesFolder')
    def getGroupWorkspacesFolder(self):
        """ Get the Group Workspaces folder object.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """
        parent = self.aq_inner.aq_parent
        folder = getattr(parent, self.getGroupWorkspacesFolderId(), None)
        return folder

    security.declareProtected(ManagePortal, 'toggleGroupWorkspacesCreation')
    def toggleGroupWorkspacesCreation(self, REQUEST=None):
        """ Toggles the flag for creation of a GroupWorkspaces folder upon creation of the group. """
        if not hasattr(self, 'groupWorkspacesCreationFlag'):
            self.groupWorkspacesCreationFlag = 0

        self.groupWorkspacesCreationFlag = not self.groupWorkspacesCreationFlag

        m = self.groupWorkspacesCreationFlag and 'turned on' or 'turned off'

        return self.manage_config(manage_tabs_message="Workspaces creation %s" % m)

    security.declareProtected(ManagePortal, 'getGroupWorkspacesCreationFlag')
    def getGroupWorkspacesCreationFlag(self):
        """Return the (boolean) flag indicating whether the Groups Tool will create a group workspace
        upon the creation of the group (if one doesn't exist already). """
        return self.groupWorkspacesCreationFlag

    security.declareProtected(AddGroups, 'createGrouparea')
    def createGrouparea(self, id):
        """Create a space in the portal for the given group, much like member home
        folders."""
        parent = self.aq_inner.aq_parent
        workspaces = self.getGroupWorkspacesFolder()
        pt = getToolByName( self, 'portal_types' )

        if id and self.getGroupWorkspacesCreationFlag():
            if workspaces is None:
                # add GroupWorkspaces folder
                pt.constructContent(
                    type_name = self.getGroupWorkspaceContainerType(),
                    container = parent,
                    id = self.getGroupWorkspacesFolderId(),
                    )
                workspaces = self.getGroupWorkspacesFolder()
                workspaces.setTitle(self.getGroupWorkspacesFolderTitle())
                workspaces.setDescription("Container for " + self.getGroupWorkspacesFolderId())
                # how about ownership?

                # this stuff like MembershipTool...
                portal_catalog = getToolByName( self, 'portal_catalog' )
                portal_catalog.unindexObject(workspaces)     # unindex GroupWorkspaces folder
                workspaces._setProperty('right_slots', (), 'lines')

            if workspaces is not None and not hasattr(workspaces, id):
                # add workspace to GroupWorkspaces folder
                pt.constructContent(
                    type_name = self.getGroupWorkspaceType(),
                    container = workspaces,
                    id = id,
                    )
                space = self.getGroupareaFolder(id)
                space.setTitle("%s workspace" % id)
                space.setDescription("Container for objects shared by this group")

                if hasattr(space, 'setInitialGroup'):
                    # GroupSpaces can have their own policies regarding the group
                    # that they are created for.
                    user = self.getGroupById(id).getGroup()
                    if user is not None:
                        space.setInitialGroup(user)
                else:
                    space.manage_delLocalRoles(space.users_with_local_role('Owner'))
                    self.setGroupOwnership(self.getGroupById(id), space)
                portal_catalog = getToolByName( self, 'portal_catalog' )
                portal_catalog.reindexObject(space)
 
    security.declareProtected(ManagePortal, 'getGroupWorkspaceType')
    def getGroupWorkspaceType(self):
        """Return the Type (as in TypesTool) to make the GroupWorkspace."""
        return self.groupWorkspaceType

    security.declareProtected(ManagePortal, 'setGroupWorkspaceType')
    def setGroupWorkspaceType(self, type):
        """Set the Type (as in TypesTool) to make the GroupWorkspace."""
        self.groupWorkspaceType = type

    security.declareProtected(ManagePortal, 'getGroupWorkspaceContainerType')
    def getGroupWorkspaceContainerType(self):
        """Return the Type (as in TypesTool) to make the GroupWorkspace."""
        return self.groupWorkspaceContainerType

    security.declareProtected(ManagePortal, 'setGroupWorkspaceContainerType')
    def setGroupWorkspaceContainerType(self, type):
        """Set the Type (as in TypesTool) to make the GroupWorkspace."""
        self.groupWorkspaceContainerType = type

    security.declarePublic('getGroupareaFolder')
    def getGroupareaFolder(self, id=None, verifyPermission=0):
        """Returns the object of the group's work area."""
        if id is None:
            group = self.getAuthenticatedMember()
            if not hasattr(member, 'getGroupId'):
                return None
            id = group.getGroupId()
        workspaces = self.getGroupWorkspacesFolder()
        if workspaces:
            try:
                folder = workspaces[id]
                if verifyPermission and not _checkPermission('View', folder):
                    # Don't return the folder if the user can't get to it.
                    return None
                return folder
            except KeyError: pass
        return None

    security.declarePublic('getGroupareaURL')
    def getGroupareaURL(self, id=None, verifyPermission=0):
        """Returns the full URL to the group's work area."""
        ga = self.getGroupareaFolder(id, verifyPermission)
        if ga is not None:
            return ga.absolute_url()
        else:
            return None

    security.declarePrivate('wrapGroup')
    def wrapGroup(self, g, wrap_anon=0):
        ''' Sets up the correct acquisition wrappers for a user
        object and provides an opportunity for a portal_memberdata
        tool to retrieve and store member data independently of
        the user object.
        '''
        b = getattr(g, 'aq_base', None)
        if b is None:
            # u isn't wrapped at all.  Wrap it in self.acl_users.
            b = g
            g = g.__of__(self.acl_users)
        if (b is nobody and not wrap_anon) or hasattr(b, 'getMemberId'):
            # This user is either not recognized by acl_users or it is
            # already registered with something that implements the
            # member data tool at least partially.
            return g

        parent = self.aq_inner.aq_parent
        base = getattr(parent, 'aq_base', None)
        if hasattr(base, 'portal_groupdata'):
##             # Apply any role mapping if we have it
##             if hasattr(self, 'role_map'):
##                 for portal_role in self.role_map.keys():
##                     if (self.role_map.get(portal_role) in u.roles and
##                             portal_role not in u.roles):
##                         u.roles.append(portal_role)

            # Get portal_groupdata to do the wrapping.
            gd = getToolByName(parent, 'portal_groupdata')
            try:
                #log("wrapping group %s" % g)
                portal_group = gd.wrapGroup(g)

                # Check for the member area creation flag and
                # take appropriate (non-) action

                # DISABLED: do it upon group creation
                #if self.getGroupWorkspacesCreationFlag():
                #    self.createGrouparea(portal_group.getGroupName())

                return portal_group

            except:
                from zLOG import LOG, ERROR
                import sys
                type,value,tb = sys.exc_info()
                try:
                    LOG('GroupsTool', ERROR, 'Error during wrapGroup:', "\nType:%s\nValue:%s\n" % (type,value))
                finally:
                    tb = None       # Avoid leaking frame
                pass
        # Failed.
        return g



InitializeClass(GroupsTool)
