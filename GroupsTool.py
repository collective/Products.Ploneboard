##############################################################################
#
# Copyright (c) 2003 Connexions Projects and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic usergroup tool.

$Id: GroupsTool.py,v 1.7 2003/07/31 01:06:20 jccooper Exp $
"""

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import SetOwnPassword
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from interfaces.portal_groups import portal_groups as IGroupsTool
     

class GroupsTool (UniqueObject, SimpleItem, ActionProviderBase):
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

    groupworkspaces_id = "GroupWorkspaces"
    groupWorkspacesCreationFlag = 1
    groupWorkspaceType = "Folder"

    manage_options=( ActionProviderBase.manage_options + 
                   ( { 'label' : 'Overview'
                     , 'action' : 'manage_overview'
                     },
                   ) + SimpleItem.manage_options)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainGroupsTool', globals())

    def getGroupById(self, id):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""
        print "getGroupById: " + id
	if id==None:
		return None
        prefix = self.acl_users.getGroupPrefix()
        g = self.acl_users.getGroup(id, prefixed=id.startswith(prefix))
        if g is not None:
	    print "getGroupById: wrapping"
            g = self.wrapGroup(g)
        return g

    def listGroups(self):
        """Returns a list of the available portal_groupdata-ish objects."""
	return [self.wrapGroup(elt) for elt in self.acl_users.getGroups()]

    def listGroupIds(self):
        """Returns a list of the available groups' ids as entered (without group prefixes)."""
        return self.acl_users.getGroupNames(prefixed=0)

    def searchForGroups(self, REQUEST, **kw):
	"""Return a list of groups meeting certain conditions. """
	# arguments need to be better refined?
        if REQUEST:
            dict = REQUEST
        else:
            dict = kw

        name = dict.get('name', None)
        email = dict.get('email', None)
        roles = dict.get('roles', None)
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
            if last_login_time:
                if g.last_login_time < last_login_time:
                    continue
            res.append(g)

        return res

    def addGroup(self, id, password, roles, domains):
        """Create a group with the supplied id, roles, and domains.

	Underlying user folder must support adding users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""
	self.acl_users.Groups.acl_users.userFolderAddUser(id, password, roles, domains)

    def editGroup(self, id, password, roles, permissions):
        """Edit the given group with the supplied password, roles, and domains.

	Underlying user folder must support editing users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""
	self.acl_users.Groups.acl_users.userFolderEditUser(id, password, roles, permissions)

    def removeGroups(self, ids):
        """Remove the group in the provided list (if possible).

	Underlying user folder must support removing users via the usual Zope API."""
	self.acl_users.Groups.acl_users.userFolderDelUsers(ids)

    def setGroupWorkspacesFolder(self, id=""):
    	""" Set the location of the Group Workspaces folder by id.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders.

     	If anyone really cares, we can probably make the id work as a path as well,
     	but for the moment it's only an id for a folder in the portal root, just like the
     	corresponding MembershipTool functionality. """
    	self.groupworkspaces_id = id.strip()

    def getGroupWorkspacesFolderId(self):
	""" Get the Group Workspaces folder object's id.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders. """
        return self.groupworkspaces_id

    def getGroupWorkspacesFolder(self):
	""" Get the Group Workspaces folder object.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders. """
    	parent = self.aq_inner.aq_parent
        folder = getattr(parent, self.getGroupWorkspacesFolderId(), None)
        return folder

    def toggleGroupWorkspacesCreation(self):
    	""" Toggles the flag for creation of a GroupWorkspaces folder upon first
        use of the group. """
        if not hasattr(self, 'groupWorkspacesCreationFlag'):
            self.groupWorkspacesCreationFlag = 0

        self.groupWorkspacesCreationFlag = not self.groupWorkspacesCreationFlag

        m = self.groupWorkspacesCreationFlag and 'turned on' or 'turned off'

        return MessageDialog(
               title  ='Group Workspaces creation flag changed',
               message='Group Workspaces creation flag has been %s' % m,
               action ='manage_mapRoles')

    def getGroupWorkspacesCreationFlag(self):
    	"""Return the (boolean) flag indicating whether the Groups Tool will create a group workspace
        upon the next use of the group (if one doesn't exist). """
        return self.groupWorkspacesCreationFlag

    def createGrouparea(self, id):
        """Create a space in the portal for the given group, much like member home
        folders."""
        print "createGrouparea: making grouparea"
	parent = self.aq_inner.aq_parent
        workspaces = self.getGroupWorkspacesFolder()
        pt = getToolByName( self, 'portal_types' )

        if id and self.getGroupWorkspacesCreationFlag():
        	print "createGrouparea: okay to make"
	        if workspaces is None:
        		# add GroupWorkspaces folder
                        print "createGrouparea: add GroupWorkspaces folder"
			parent.invokeFactory("Folder", self.getGroupWorkspacesFolderId())

        	if workspaces is not None and not hasattr(workspaces, id):
                	# add workspace to GroupWorkspaces folder
                        print "createGrouparea: add workspace to GroupWorkspaces folder"
                        workspace =self.getGroupWorkspacesFolder()
                        workspace.invokeFactory(self.getGroupWorkspaceType(), id)
	print "createGrouparea: done"

    def getGroupWorkspaceType(self):
	"""Return the Type (as in TypesTool) to make the GroupWorkspace."""
        return self.groupWorkspaceType

    def setGroupWorkspaceType(self, type):
	"""Set the Type (as in TypesTool) to make the GroupWorkspace."""
	self.groupWorkspaceType = type

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

    def getGroupareaURL(self, id=None, verifyPermission=0):
            """Returns the full URL to the group's work area."""
	    ga = self.getGroupareaFolder(id, verifyPermission)
	    if ga is not None:
	        return ga.absolute_url()
	    else:
	        return None


    security.declarePrivate('wrapUser')
    def wrapGroup(self, g, wrap_anon=0):
        ''' Sets up the correct acquisition wrappers for a user
        object and provides an opportunity for a portal_memberdata
        tool to retrieve and store member data independently of
        the user object.
        '''
        print "wrapGroup: start"
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
            	print "wrapGroup: wrapping group"
                portal_group = gd.wrapGroup(g)

                # Check for the member area creation flag and
                # take appropriate (non-) action
                if self.getGroupWorkspacesCreationFlag():
			print "wrapGroup: creating grouparea"
                	self.createGrouparea(portal_group.getGroupName())

                return portal_group

            except:
                from zLOG import LOG, ERROR
                import sys
                type,value,tb = sys.exc_info()
                try:
                    LOG('GroupsTool', ERROR, 'Error during wrapUser:', "\nType:%s\nValue:%s\n" % (type,value))
                finally:
                    tb = None       # Avoid leaking frame
                pass
        # Failed.
        return g

InitializeClass(GroupsTool)
