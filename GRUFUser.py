##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Ingeniweb SARL
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
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
from zExceptions import Unauthorized
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
##                    'authenticate', '_shared_roles', 'changePassword',
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
    def __init__(self, underlying_user, GRUF, isGroup = 0):
        # When calling, set isGroup it to TRUE if this user represents a group
        self._setUnderlying(underlying_user)
        self._isGroup = isGroup   
        self._GRUF = GRUF
        self.id = self._original_id

    security.declarePublic('isGroup')
    def isGroup(self,):
        """Return 1 if this user is a group abstraction"""
        return self._isGroup

    security.declarePrivate('getGroups')
    def getGroups(self):
        """
        If this user is a user (uh, uh), get its groups.
        $$$ BY NOW, WE DO NOT AUTHORIZE GROUPS TO BELONG TO GROUPS. 
        This excludes 'group inheritance'.
        Maybe we could authorize this one day, then we should 
        modify this behaviour.

        This method is private and should remain so.
        """
        # List this user's roles. We consider that roles starting 
        # with _group_prefix are in fact groups, and thus are 
        # returned (prefixed).
        ret = []
        prefix = GRUFFolder.GRUFGroups._group_prefix
        for role in self._original_roles:
            if string.find(role, prefix) == 0:
                ret.append(role)
        return tuple(ret)


    security.declarePrivate('getGroupsWithoutPrefix')
    def getGroupsWithoutPrefix(self,):
        """
        Same as getGroups but return them without a prefix.
        """
        ret = []
        for group in self.getGroups():
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
          self._original_name[:len(grufprefix)]!=grufprefix:
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
        user = []
        groups = []
        prefix = GRUFFolder.GRUFGroups._group_prefix

        # Get user roles
        for role in self._original_roles:
            if string.find(role, grufprefix) != 0:
                user.append(role)

        # Get group roles
        groups = self.getGroupRoles()

        # Return user and groups roles
        return GroupUserFolder.unique(tuple(user) + tuple(groups))

    security.declarePublic('getUserRoles')
    def getUserRoles(self):
        """
        returns the roles defined for the user without the group roles
        """
        prefix=GRUFFolder.GRUFGroups._group_prefix
        return [r for r in self._original_roles if not r.startswith(prefix)]

    security.declarePublic("getGroupRoles")
    def getGroupRoles(self,):
        """
        Return the tuple of roles belonging to this user's group(s)
        """
        ret = []
        groups = self._GRUF.acl_users.getGroupNames()
        
        for group in self.getGroups():
            if not group in groups:
                Log("Group", group, "is invalid. Ignoring.")
                # This may occur when groups are deleted
                # Ignored silently
                continue  
            ret.extend(self._GRUF.acl_users.getGroup(group).getRoles())
            
        return GroupUserFolder.unique(ret)
    
    security.declarePublic('getRolesInContext')
    def getRolesInContext(self, object, userid = None):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""
        if not userid:
            userid=self.getId()
        roles=self.getRoles()
        group_roles = []
        local={}
        object=getattr(object, 'aq_inner', object)
        while 1:
            # Get local roles for this user
            local_roles = getattr(object, '__ac_local_roles__', None)
            if local_roles:
                if callable(local_roles):
                    local_roles=local_roles()
                dict=local_roles or {}
                for r in dict.get(userid, []):
                    local[r]=1

                # Get roles & local roles for groups
                for groupid in self.getGroups():
                    for r in dict.get(groupid, []):
                        group_roles.append(r)

            # Prepare next iteration
            inner = getattr(object, 'aq_inner', object)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                object = parent
                continue
            if hasattr(object, 'im_self'):
                object=object.im_self
                object=getattr(object, 'aq_inner', object)
                continue
            break
        
        roles=list(roles) + local.keys() + group_roles
        return GroupUserFolder.unique(roles)

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
        if self._isGroup():
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

        # Check for a role match with the normal roles given to
        # the user, then with local roles only if necessary. We
        # want to avoid as much overhead as possible.
        user_roles = self.getRoles()
        for role in object_roles:
            if role in user_roles:
                if self._check_context(object):
                    return 1
                return None

        # Check against getRolesInContext
        # This is time-consuming, it may be possible to avoid several
        # tests by copying the original allowed() implemetation from
        # AccessControl.User and adapting it to GRUF needs.
        # So, the following code works but can be optimized.
        for role in self.getRolesInContext(object):
            if role in object_roles:
                return 1
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

    security.declarePublic('__getattr__')
    def __getattr__(self, name):
        # This will call the underlying object's methods
        # if they are not found in this user object.
        Log(LOG_DEBUG, "Trying to get attribute", name)
        try:
            return self.__dict__['__underlying__'].restrictedTraverse(name)
        except AttributeError:
            # Use a try/except to fetch attributes from UserFolders that
            # do not handle restrictedTraverse
            try:
                return getattr(self.__dict__['__underlying__'], name)
            except:
                # Use acquisition regularily
                # XXX Have to check security on this !!!
                return self.inheritedAttribute(GRUFUser, name)
