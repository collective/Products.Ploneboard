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

from Globals import MessageDialog, DTMLFile      # fakes a method from a DTML file
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import Implicit
from Globals import Persistent
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item
from OFS.PropertyManager import PropertyManager
import OFS
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
from AccessControl.PermissionRole import _what_not_even_god_should_do, rolesForPermissionOn



class GRUFUser(AccessControl.User.BasicUser, Implicit):         #Persistent):
    """
    Base class for all GRUF-catched User objects.
    There's, alas, many copy/paste from AccessControl.BasicUser...
    """

    def _setUnderlying(self, user):
        """
        _setUnderlying(self, user) => Set the GRUFUser properties to the underlying user's one.
        Be careful that any change to the underlying user won't be reported here. $$$ We don't know yet if User object are transaction-persistant or not...
        """
        self._original_name   = user.getUserName()
        self._original_password = user._getPassword()
        self._original_roles = user.getRoles()
        self._original_domains = user.getDomains()
        self._original_id = user.getId()
        self.__underlying__ = user                              # $$$ Used only for authenticate()

##        self.__underlying__ = user
##        self.__underlying__.getPhysicalRoot = self._user_fake_getPhysicalRoot
##        self.__underlying__.id = "acl_users"  ##self.getGRUFId()

##    def _user_fake_getPhysicalRoot(self,):                                      # $$$ Trick for getPhysicalRoot
##        Log(LOG_DEBUG, "within _user_fake_getPhysicalRoot", self.getId(), )
##        return "/"

##    def _user_fake_id(self,):
##        """faking the 'id' attribute for Owned.py module / ownerInfo method"""
##        Log(LOG_DEBUG, "Within fake_id")
##        return """__VERY_BAD_VALUE__"""

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
    def __allow_access_to_unprotected_subobjects__(self, name, value=None):
        deny_names=('name', '__', 'roles', 'domains', '_getPassword',
                    'authenticate', '_shared_roles')
        if name in deny_names:
            return 0
        return 1

##    def __init__(self,name,password,roles,domains):
##        raise NotImplemented

    def __init__(self, underlying_user, GRUF, isGroup = 0):
        self._setUnderlying(underlying_user)
        self._isGroup = isGroup                         # Set it to TRUE if this user represents a group
        self._GRUF = GRUF
        self.id = self._original_id

    def isGroup(self,):
        """Return 1 if this user is a group abstraction"""
        return self._isGroup

    def getGroups(self,):
        """
        If this user is a user (uh, uh), get its groups.
        $$$ BY NOW, WE DO NOT AUTHORIZE GROUPS TO BELONG TO GROUPS. This excludes 'group inheritance'.
        Maybe we could authorize this one day, then we should modify this behaviour.
        """
        # List this user's roles. We consider that roles starting with _group_prefix are in fact groups, and thus are returned (prefixed).
        ret = []
        prefix = GRUFFolder.GRUFGroups._group_prefix
        for role in self._original_roles:
            if string.find(role, prefix) == 0:
                ret.append(role)
        return tuple(ret)

    def getUserName(self):
        """Return the username of a user"""
        if self.isGroup():
            return "%s%s" % (GRUFFolder.GRUFGroups._group_prefix, self._original_name, )
        return self._original_name

    def getId(self):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's
        UserDatabase"""
        # $$$ OUT TO DATE
##        # Prevent storage of a GRUFUser as underlying object
##        if not hasattr(self.__underlying__.aq_base, 'getGroups'):
##            return self._original_id

        # Return the right id
        if self.isGroup():
            return "%s%s" % (GRUFFolder.GRUFGroups._group_prefix, self._original_id, )
        return self._original_id

    def _getPassword(self):
        """Return the password of the user."""
        return self._original_password

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
            if string.find(role, prefix) != 0:
                user.append(role)

        # Get group roles
        groups = self.getGroupRoles()

        # Return user and groups roles
        return GroupUserFolder.unique(tuple(user) + tuple(groups))


    def getGroupRoles(self,):
        """
        Return the tuple of roles belonging to this user's group(s)
        """
        ret = []
        groups = self._GRUF.acl_users.getGroupNames()
        
        for group in self.getGroups():
            if not group in groups:
                Log("Group", group, "is invalid. Ignoring.")
                continue                # This may occur when groups are deleted. Ignored silently
            ret.extend(self._GRUF.acl_users.getGroup(group).getRoles())
            
        return GroupUserFolder.unique(ret)
    

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
##                        group_roles.extend(self._GRUF.getGroup(groupid).getRolesInContext(object))            $$$ Removed for performance reasons, seems to work ! ;-)

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

    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        return self._original_domains

    # ------------------------------
    # Internal User object interface
    # ------------------------------

    def authenticate(self, password, request):
        return self.__underlying__.authenticate(password, request)


    def allowed(self, object, object_roles=None):
        """Check whether the user has access to object. The user must
           have one of the roles in object_roles to allow access."""

        if object_roles is _what_not_even_god_should_do: return 0

        # Short-circuit the common case of anonymous access.
        if object_roles is None or 'Anonymous' in object_roles:
            return 1

        # Provide short-cut access if object is protected by 'Authenticated'
        # role and user is not nobody
        if 'Authenticated' in object_roles and (
            self.getUserName() != 'Anonymous User'):
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

        # Check violently against getRolesInContext ($$$ may have to copy/paste code here to improve performance)
        for role in self.getRolesInContext(object):
            if role in object_roles:
                return 1

##        # Still have not found a match, so check local roles. We do
##        # this manually rather than call getRolesInContext so that
##        # we can incur only the overhead required to find a match.
##        inner_obj = getattr(object, 'aq_inner', object)
##        userid = self.getId()
##        while 1:
##            local_roles = getattr(inner_obj, '__ac_local_roles__', None)
##            if local_roles:
##                if callable(local_roles):
##                    local_roles = local_roles()
##                dict = local_roles or {}
##                local_roles = dict.get(userid, [])
##                for role in object_roles:
##                    if role in local_roles:
##                        if self._check_context(object):
##                            return 1
##                        return 0
##            inner = getattr(inner_obj, 'aq_inner', inner_obj)
##            parent = getattr(inner, 'aq_parent', None)
##            if parent is not None:
##                inner_obj = parent
##                continue
##            if hasattr(inner_obj, 'im_self'):
##                inner_obj=inner_obj.im_self
##                inner_obj=getattr(inner_obj, 'aq_inner', inner_obj)
##                continue
##            break
        return None

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

##    domains=[]

##    def has_role(self, roles, object=None):
##        """Check to see if a user has a given role or roles."""
##        if type(roles)==type('s'):
##            roles=[roles]
##        if object is not None:
##            user_roles = self.getRolesInContext(object)
##        else:
##            # Global roles only...
##            user_roles=self.getRoles()
##        for role in roles:
##            if role in user_roles:
##                return 1
##        return 0

##    def has_permission(self, permission, object):
##        """Check to see if a user has a given permission on an object."""
##        return getSecurityManager().checkPermission(permission, object)

##    def __len__(self): return 1
##    def __str__(self): return self.getUserName()
##    __repr__=__str__

