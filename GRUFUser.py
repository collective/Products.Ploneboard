##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL
#
##############################################################################

"""GroupUserFolder product"""
# fakes a method from a DTML File
from Globals import MessageDialog, DTMLFile 

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from Globals import InitializeClass
from Acquisition import Implicit, aq_inner, aq_parent, aq_base
from Globals import Persistent
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item
from OFS.PropertyManager import PropertyManager
from OFS import ObjectManager, SimpleItem
from DateTime import DateTime
from App import ImageFile
import AccessControl.Role, webdav.Collection
import Products
import os
import string
import shutil
import random
from global_symbols import *
import AccessControl
import GRUFFolder
import GroupUserFolder
from AccessControl.PermissionRole \
  import _what_not_even_god_should_do, rolesForPermissionOn
from ComputedAttribute import ComputedAttribute


import os
import traceback


# NOTE : _what_not_even_god_should_do is a specific permission defined by ZOPE
# that indicates that something has not to be done within Zope.
# This value is given to the ACCESS_NONE directive of a SecurityPolicy.
# It's rarely used within Zope BUT as it is documented (in AccessControl)
# and may be used by third-party products, we have to process it.


#GRUFPREFIX is a constant
grufprefix = GRUFFolder.GRUFGroups._group_prefix
_group_prefix = GRUFFolder.GRUFGroups._group_prefix

class GRUFUser(AccessControl.User.BasicUser, Implicit): 
    """
    Base class for all GRUF-catched User objects.
    There's, alas, many copy/paste from AccessControl.BasicUser...
    """

    security = ClassSecurityInfo()

##    def __allow_access_to_unprotected_subobjects__(self, name, value=None):
##        # This is get back from AccessControl.User.BasicUser
##        deny_names=('name', '__', 'roles', 'domains', '_getPassword',
##                    'authenticate', '_shared_roles', 
##                    "_setUnderlying", "__init__", )
##        if name in deny_names:
##            return 0
##        return 1

    security.declarePrivate('_setUnderlying')
    def _setUnderlying(self, user):
        """
        _setUnderlying(self, user) => Set the GRUFUser properties to 
        the underlying user's one.
        Be careful that any change to the underlying user won't be 
        reported here. $$$ We don't know yet if User object are 
        transaction-persistant or not...
        """
        self._original_name   = user.getUserName()
        self._original_password = user._getPassword()
        self._original_roles = user.getRoles()
        self._original_domains = user.getDomains()
        self._original_id = user.getId()
        self.__underlying__ = user # Used for authenticate() and __getattr__


    # ----------------------------
    # Public User object interface
    # ----------------------------

    # Maybe allow access to unprotected attributes. Note that this is
    # temporary to avoid exposing information but without breaking
    # everyone's current code. In the future the security will be
    # clamped down and permission-protected here. Because there are a
    # fair number of user object types out there, this method denies
    # access to names that are private parts of the standard User
    # interface or implementation only. The other approach (only
    # allowing access to public names in the User interface) would
    # probably break a lot of other User implementations with extended
    # functionality that we cant anticipate from the base scaffolding.

    security.declarePrivate('__init__')
    def __init__(self, underlying_user, GRUF, isGroup = 0, source_id = 'Users', ):
        # When calling, set isGroup it to TRUE if this user represents a group
        self._setUnderlying(underlying_user)
        self._isGroup = isGroup   
        self._GRUF = GRUF
        self._source_id = source_id
        self.id = self._original_id
        # Store the results of getRoles and getGroups. Initially set to None,
        # set to a list after the methods are first called.
        # If you are caching users you want to clear these.
        self.clearCachedGroupsAndRoles()

    security.declarePrivate('clearCachedGroupsAndRoles')
    def clearCachedGroupsAndRoles(self, underlying_user = None):
        self._groups = None
        self._user_roles = None
        self._group_roles = None
        self._all_roles = None
        if underlying_user:
            self._setUnderlying(underlying_user)

    security.declarePublic('isGroup')
    def isGroup(self,):
        """Return 1 if this user is a group abstraction"""
        return self._isGroup

    security.declarePublic('getUserSourceId')
    def getUserSourceId(self,):
        """
        getUserSourceId(self,) => string
        Return the GRUF's GRUFUsers folder used to fetch this user.
        """
        return self._source_id

    security.declarePrivate('getGroups')
    def getGroups(self, no_recurse = 0, already_done = [], prefix = GRUFFolder.GRUFGroups._group_prefix):
        """
        getGroups(self, no_recurse = 0, already_done = [], prefix = GRUFFolder.GRUFGroups._group_prefix) => list of strings
        
        If this user is a user (uh, uh), get its groups.
        THIS METHODS NOW SUPPORTS NESTED GROUPS ! :-)
        The already_done parameter prevents infite recursions.
        Keep it as it is, never give it a value.

        If no_recurse is true, return only first level groups

        This method is private and should remain so.
        """
        # List this user's roles. We consider that roles starting 
        # with _group_prefix are in fact groups, and thus are 
        # returned (prefixed).
        if self._groups is not None:
            return self._groups

        ret = []

        # Scan roles to find groups
        for role in self._original_roles:
            # Inspect group-like roles
            if role.startswith(prefix):
                
                # Prevent infinite recursion
                if self._isGroup and role in already_done:
                    continue 
                    
                # Get the underlying group
                grp = self.aq_parent.getUser(role)
                if not grp:
                    continue    # Invalid group

                # Do not add twice the current group
                if role in ret:
                    continue

                # Append its nested groups (if recurse is asked)
                ret.append(role)
                if no_recurse:
                    continue
                for extend in grp.getGroups(already_done = ret):
                    if not extend in ret:
                        ret.append(extend)

        # Return the groups
        self._groups = tuple(ret)
        return self._groups


    security.declarePrivate('getGroupsWithoutPrefix')
    def getGroupsWithoutPrefix(self, **kw):
        """
        Same as getGroups but return them without a prefix.
        """
        ret = []
        for group in self.getGroups(**kw):
          if group.startswith(grufprefix):
            ret.append(group[len(grufprefix):])
        return ret
                
    security.declarePublic('getUserNameWithoutGroupPrefix')
    def getUserNameWithoutGroupPrefix(self):
        """Return the username of a user without a group prefix"""
        if self.isGroup() and \
          self._original_name[:len(grufprefix)] == grufprefix:
            return self._original_name[len(grufprefix):]
        return self._original_name

    security.declarePublic('getUserName')
    def getUserName(self):
        """Return the username of a user"""
        if self.isGroup() and \
          not self._original_name[:len(grufprefix)] == grufprefix:
            return "%s%s" % (grufprefix, self._original_name )
        return self._original_name

    security.declarePublic('getId')
    def getId(self):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's UserDatabase 
        """
        # Return the right id
        if self.isGroup() and \
          self._original_name[:len(grufprefix)] != grufprefix:
            return "%s%s" % (grufprefix, self._original_name)
        return self._original_name

    security.declarePrivate('_getPassword')
    def _getPassword(self):
        """Return the password of the user."""
        return self._original_password

    security.declarePublic('getRoles')
    def getRoles(self):
        """
        Return the list (tuple) of roles assigned to a user.
        THIS IS WHERE THE ATHENIANS REACHED !
        """
        if self._all_roles is not None:
            return self._all_roles

        # Return user and groups roles
        self._all_roles = GroupUserFolder.unique(self.getUserRoles() + self.getGroupRoles())
        return self._all_roles

    security.declarePublic('getUserRoles')
    def getUserRoles(self):
        """
        returns the roles defined for the user without the group roles
        """
        if self._user_roles is not None:
            return self._user_roles
        prefix=GRUFFolder.GRUFGroups._group_prefix
        self._user_roles = tuple([r for r in self._original_roles if not r.startswith(prefix)])
        return self._user_roles

    security.declarePublic("getGroupRoles")
    def getGroupRoles(self,):
        """
        Return the tuple of roles belonging to this user's group(s)
        """
        if self._group_roles is not None:
            return self._group_roles
        ret = []
        acl_users = self._GRUF.acl_users 
        groups = acl_users.getGroupNames()
        
        for group in self.getGroups():
            if not group in groups:
                Log("Group", group, "is invalid. Ignoring.")
                # This may occur when groups are deleted
                # Ignored silently
                continue
            ret.extend(acl_users.getGroup(group).getUserRoles())
        
        self._group_roles = GroupUserFolder.unique(ret)
        return self._group_roles
    
    security.declarePublic('getRolesInContext')
    def getRolesInContext(self, object, userid = None):
        """
        Return the list of roles assigned to the user,
        including local roles assigned in context of
        the passed in object.
        """
        if not userid:
            userid=self.getId()

        roles = {}
        for role in self.getRoles():
            roles[role] = 1

        user_groups = self.getGroups()

        inner_obj = getattr(object, 'aq_inner', object)
        while 1:
            local_roles = getattr(inner_obj, '__ac_local_roles__', None)
            if local_roles:
                if callable(local_roles):
                    local_roles = local_roles()
                dict = local_roles or {}

                for role in dict.get(userid, []):
                    roles[role] = 1

                # Get roles & local roles for groups
                # This handles nested groups as well
                for groupid in user_groups:
                    for role in dict.get(groupid, []):
                        roles[role] = 1

            inner = getattr(inner_obj, 'aq_inner', inner_obj)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                inner_obj = parent
                continue
            if hasattr(inner_obj, 'im_self'):
                inner_obj=inner_obj.im_self
                inner_obj=getattr(inner_obj, 'aq_inner', inner_obj)
                continue
            break
        
        return tuple(roles.keys())

    security.declarePublic('getDomains')
    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        return self._original_domains

    # ------------------------------
    # Internal User object interface
    # ------------------------------

    security.declarePrivate('authenticate')
    def authenticate(self, password, request):
        # We prevent groups from authenticating
        if self._isGroup:
            return None
        return self.__underlying__.authenticate(password, request)


    security.declarePublic('allowed')
    def allowed(self, object, object_roles=None):
        """Check whether the user has access to object. The user must
           have one of the roles in object_roles to allow access."""

        if object_roles is _what_not_even_god_should_do: 
            return 0

        # Short-circuit the common case of anonymous access.
        if object_roles is None or 'Anonymous' in object_roles:
            return 1

        # Provide short-cut access if object is protected by 'Authenticated'
        # role and user is not nobody
        if 'Authenticated' in object_roles and \
            (self.getUserName() != 'Anonymous User'):
            return 1

        # Check for ancient role data up front, convert if found.
        # This should almost never happen, and should probably be
        # deprecated at some point.
        if 'Shared' in object_roles:
            object_roles = self._shared_roles(object)
            if object_roles is None or 'Anonymous' in object_roles:
                return 1


        # Trying to make some speed improvements, changes starts here.
        # Helge Tesdal, Plone Solutions AS, http://www.plonesolutions.com
        # We avoid using the getRoles() and getRolesInContext() methods to be able
        # to short circuit.
        
        # Dict for faster lookup and avoiding duplicates
        object_roles_dict = {}
        for role in object_roles:
            object_roles_dict[role] = 1

        if [role for role in self.getUserRoles() if object_roles_dict.has_key(role)]:
            if self._check_context(object):
                return 1
            return None

        # Try the top level group roles.
        if [role for role in self.getGroupRoles() if object_roles_dict.has_key(role)]:
            if self._check_context(object):
                return 1
            return None

        user_groups = self.getGroups()
        # No luck on the top level, try local roles
        inner_obj = getattr(object, 'aq_inner', object)
        userid = self.getId()
        while 1:
            local_roles = getattr(inner_obj, '__ac_local_roles__', None)
            if local_roles:
                if callable(local_roles):
                    local_roles = local_roles()
                dict = local_roles or {}

                if [role for role in dict.get(userid, []) if object_roles_dict.has_key(role)]:
                    if self._check_context(object):
                        return 1
                    return None

                # Get roles & local roles for groups
                # This handles nested groups as well
                for groupid in user_groups:
                    if [role for role in dict.get(groupid, []) if object_roles_dict.has_key(role)]:
                        if self._check_context(object):
                            return 1
                        return None

            inner = getattr(inner_obj, 'aq_inner', inner_obj)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                inner_obj = parent
                continue
            if hasattr(inner_obj, 'im_self'):
                inner_obj=inner_obj.im_self
                inner_obj=getattr(inner_obj, 'aq_inner', inner_obj)
                continue
            break
        return None
    

    security.declarePublic('hasRole')
    def hasRole(self, *args, **kw):
        """hasRole is an alias for 'allowed' and has been deprecated.

        Code still using this method should convert to either 'has_role' or
        'allowed', depending on the intended behaviour.

        """
        import warnings
        warnings.warn('BasicUser.hasRole is deprecated, please use '
            'BasicUser.allowed instead; hasRole was an alias for allowed, but '
            'you may have ment to use has_role.', DeprecationWarning)
        return self.allowed(*args, **kw)

    security.declareProtected(Permissions.manage_users, 'getGroupUsers')
    def getGroupUsers(self):
        '''
        returns the users belonging to this group.
        '''
        if not self.isGroup():
            raise TypeError,'This method only aplies to groups'
        
        return [u for u in self.aq_parent.getUsers() 
                if self.getId() in u.getGroups()]


    #                                                           #
    #               Underlying user object support              #
    #                                                           #

##    security.declarePublic('__getattr__')
##    def __getattr__(self, name):
##        # This will call the underlying object's methods
##        # if they are not found in this user object.
##        try:
##            return self.__dict__['__underlying__'].restrictedTraverse(name)
##        except AttributeError:
##            # Use a try/except to fetch attributes from UserFolders that
##            # do not handle restrictedTraverse
##            try:
##                return getattr(self.__dict__['__underlying__'], name)
##            except:
##                # Use acquisition regularily
##                # XXX Have to check security on this !!!
##                return self.inheritedAttribute(GRUFUser, name)


    def __getattr__(self, name):
        # This will call the underlying object's methods
        # if they are not found in this user object.
        # We will have to check Chris' http://www.plope.com/Members/chrism/plone_on_zope_head
        # to make it work with Zope HEAD.
        ret = getattr(self.__dict__['__underlying__'], name)
        return ret

    security.declarePublic('getUnwrappedUser')
    def getUnwrappedUser(self,):
        """
        same as GRUF.getUnwrappedUser, but implicitly with this particular user
        """
        return self.__dict__['__underlying__']

    def __getitem__(self, name):
        # This will call the underlying object's methods
        # if they are not found in this user object.
        return self.__underlying__[name]
 
    #                                                           #
    #                   Password changing                       #
    #                                                           #

    security.declarePrivate('changePassword')
    def changePassword(self, password):
        """Set the user's password"""
        # don't spam the user's roles with special roles
        roles = self._original_roles  # we must keep group roles
        roles = filter(lambda x: x not in ('Authenticated', 'Shared', 'Anonymous'), roles)
        
        # set the profile on the user folder
        self.userFolderEditUser(
            self.getUserName(),
            password,
            roles,
            self.getDomains(),
            )


    #                                                           #
    #                      HTML link support                    #
    #                                                           #

    def asHTML(self, implicit=0):
        """
        asHTML(self, implicit=0) => HTML string
        Used to generate homogeneous links for management screens
        """
        acl_users = self.acl_users
        if self.isGroup():
            color = acl_users.group_color
            kind = "Group"
        else:
            color = acl_users.user_color
            kind = "User"

        ret = '''<a href="%(href)s" alt="%(alt)s"><font color="%(color)s">%(name)s</font></a>''' % {
            "color": color,
            "href": "%s/%s/manage_workspace" % (acl_users.absolute_url(), self.getId(), ),
            "name": self.getUserNameWithoutGroupPrefix(),
            "alt": "%s (%s)" % (self.getUserNameWithoutGroupPrefix(), kind, ),
            }
        if implicit:
            return "<i>%s</i>" % ret
        return ret
