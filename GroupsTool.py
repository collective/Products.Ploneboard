##############################################################################
#
# Copyright (c) 2003 Connexions Projects and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic usergroup tool.

$Id: GroupsTool.py,v 1.5 2003/07/14 23:45:00 jccooper Exp $
"""

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName, _dtmldir
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

    manage_options=( ActionProviderBase.manage_options + 
                   ( { 'label' : 'Overview'
                     , 'action' : 'manage_overview'
                     },
                   ) + SimpleItem.manage_options)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainMembershipTool', _dtmldir )

    def getGroupById(self, id):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""
	if id==None:
		return None
        prefix = self.acl_users.getGroupPrefix()
        g = self.acl_users.getGroup(id, prefixed=id.startswith(prefix))
        if g is not None:
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

##
## Group workspace stuff not yet implemented!
##

    def createGrouparea(self, id):
        """Create a space in the portal for the given group, much like member home
        folders."""
##         parent = self.aq_inner.aq_parent
##         members =  getattr(parent, 'Members', None)

##         user = self.acl_users.getUserById( member_id, None )
##         if user is None:
##             raise ValueError, 'Member %s does not exist' % member_id

##         if user is not None:
##             user = user.__of__( self.acl_users )

##         if members is not None and user is not None:
##             f_title = "%s's Home" % member_id
##             members.manage_addPortalFolder( id=member_id, title=f_title )
##             f=getattr(members, member_id)

##             f.manage_permission(View,
##                                 ['Owner','Manager','Reviewer'], 0)
##             f.manage_permission(AccessContentsInformation,
##                                 ['Owner','Manager','Reviewer'], 0)

##             # Grant ownership to Member
##             try: f.changeOwnership(user)
##             except AttributeError: pass  # Zope 2.1.x compatibility
##             f.manage_setLocalRoles(member_id, ['Owner'])



    def getGroupareaFolder(self, id):
            """Returns the object of the group's work area."""

    def getGroupareaURL(self, id):
            """Returns the full URL to the group's work area."""

    security.declarePrivate('wrapUser')
    def wrapGroup(self, g, wrap_anon=0):
        '''
        Sets up the correct acquisition wrappers for a user
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
            ## # Apply any role mapping if we have it
##             if hasattr(self, 'role_map'):
##                 for portal_role in self.role_map.keys():
##                     if (self.role_map.get(portal_role) in u.roles and
##                             portal_role not in u.roles):
##                         u.roles.append(portal_role)

            # Get portal_groupdata to do the wrapping.
            gd = getToolByName(parent, 'portal_groupdata')
            try:
                portal_group = gd.wrapGroup(g)

##                 # Check for the member area creation flag and
##                 # take appropriate (non-) action
##                 if getattr(self, 'groupareaCreationFlag', 0) != 0:
##                     if self.getHomeUrl(portal_group.getId()) is None:
##                         self.createGrouparea(portal_group.getId())

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
