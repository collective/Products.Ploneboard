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

# fakes a method from a DTML file
from Globals import MessageDialog, DTMLFile

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
import AccessControl.User
import GRUFFolder
import GRUFUser

DEBUG=1
#import zLOG
#
#def log(message,summary='',severity=0):
#    zLOG.LOG('GroupUserFolder: ',severity,summary,message)


_group_prefix_len = len(GRUFFolder.GRUFGroups._group_prefix)

def unique(sequence):
    """
    unique(sequence) => make sequence a list of unique items
    """
    ret = []
    lst = list(sequence)
    lst.sort()
    prev = "THIS VALUE WILL SURELY BE UNIQUE IN ALL THE LISTS " \
           "WE CAN IMAGINE ! :-)"
    for item in lst:
        if item == prev:
            continue
        ret.append(item)
        prev = item
    return tuple(ret)


def manage_addGroupUserFolder(self,dtself=None,REQUEST=None,**ignored):
    """ Factory method that creates a UserFolder"""
    f=GroupUserFolder()
    self=self.this()
    try:    self._setObject('acl_users', f)
    except: return MessageDialog(
                   title  ='Item Exists',
                   message='This object already contains a User Folder',
                   action ='%s/manage_main' % REQUEST['URL1'])
    self.__allow_groups__=f
    self.acl_users._post_init()

    self.acl_users.Users.manage_addUserFolder()
    self.acl_users.Groups.manage_addUserFolder()

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class GroupUserFolder(OFS.ObjectManager.ObjectManager, 
                      AccessControl.User.BasicUserFolder ):
    """
    GroupUserFolder => User folder with groups management
    """
    meta_type='Group User Folder'
    id       ='acl_users'
    title    ='Group-aware User Folder'

    isAnObjectManager=1
    isPrincipiaFolderish=1

    manage_options=( OFS.ObjectManager.ObjectManager.manage_options + \
        ( {'label':'Overview', 'action':'manage_overview'}, ) + \
        RoleManager.manage_options + \
        Item.manage_options )

    manage_main = OFS.ObjectManager.ObjectManager.manage_main
    manage_overview = DTMLFile('dtml/GroupUserFolder_overview', globals())
    manage_addUser = DTMLFile('dtml/addUser', globals())


    __ac_permissions__=(
        ('Manage users',
         ('manage_users','getUserNames', 'getUser', 'getUsers',
          'getUserById', 'user_names', 'setDomainAuthenticationMode',
          'userFolderAddUser', 'userFolderEditUser', 'userFolderDelUsers',
          'getUnwrappedUser', 'getUnwrappedGroup',
          )
         ),
        )

    # ------------------------
    #    Various operations  #
    # ------------------------
    def __init__(self):
        """
        __init__(self) -> initialization method
        We define it to prevend calling ancestor's __init__ methods.
        """
        pass


    def _post_init(self):
        """
        _post_init(self) => meant to be called when the 
                            object is in the Zope tree
        """
        uf = GRUFFolder.GRUFUsers()
        gf = GRUFFolder.GRUFGroups()
        self._setObject('Users', uf)
        self._setObject('Groups', gf)
        self.id = "acl_users"


    def getGroupPrefix(self):
        """ group prefix """
        return GRUFFolder.GRUFGroups._group_prefix
    
    def getLocalRolesForDisplay(self, object):
        result = []
        local_roles = object.get_local_roles()
        prefix = self.getGroupPrefix()
        #log('prefix is: "%s"' % (prefix,))
        for one_user in local_roles:
            massagedUsername = username = one_user[0]
            roles = one_user[1]
            userType = 'user'
            if prefix:
                #log('username is: "%s"' % (username,))
                if self.getGroup(username) or \
                   self.getGroup('%s%s' % (prefix, username)):
                    #log('found group %s' % (username,))
                    if username.startswith(prefix):
                        massagedUsername = username[len(prefix):]
                        #log('massagedUsername is: "%s"' % (massagedUsername,))
                    userType = 'group'
                #else:
                #    log('DID NOT FIND group %s' % (username,))
            else:
                userType = 'unknown'
            result.append((massagedUsername, roles, userType))
        return tuple(result)    

    def getGRUFPhysicalRoot(self,):
        # $$$ trick meant to be used within 
        # fake_getPhysicalRoot (see __init__)
        return self.getPhysicalRoot()   

    def getGRUFId(self,):
        """
        Alias to self.getId()
        """
        return self.getId()
    
    # ----------------------------------
    # Public UserFolder object interface
    # ----------------------------------

    def getUserNames(self):
        """
        Return a list of usernames (including groups).
        Fetch the list from GRUFUsers and GRUFGroups.
        """
        if not "acl_users" in self.Users.objectIds() or \
           not "acl_users" in self.Groups.objectIds():
            return ()
        return self.Users.acl_users.getUserNames() + \
               self.Groups.getGroupNames()

    def getUsers(self):
        """Return a list of user objects"""
        ret = []
        for n in self.getUserNames():
            ret.append(self.getUser(n))

        return filter(None, ret)
        # This prevents 'None' user objects to be returned. 
        # This happens for example with LDAPUserFolder when a 
        # LDAP query fetches too much records.

    def getUser(self, name):
        """Return the named user object or None"""
        # Prevent infinite recursion when instanciating a GRUF 
        # without having sub-acl_users set
        if not "acl_users" in self.Users.objectIds() or \
           not "acl_users" in self.Groups.objectIds():
            return None
        
        # Fetch users first
        u = self.Users.acl_users.getUser(name)
        if u:
            Log(LOG_DEBUG, "Returning a user object", name, u, u.__class__)
            return GRUFUser.GRUFUser(u, self,).__of__(self) 
            # $$$ Check security for this !
        
        # If not found, fetch groups (then the user must be 
        # prefixed by 'group_' prefix)

        u = self.Groups.getGroup(name)
        if u:
            Log(LOG_DEBUG, "Returning a group object", name, u)
            return GRUFUser.GRUFUser(u, self, isGroup = 1).__of__(self)
            # $$$ check security for this! and check against double 
            # GRUFUser wrapping (what getGroup() is called ?)
 
        return None


    def getUnwrappedUser(self, name):
        """
        getUnwrappedUser(self, name) => user object or None

        This method is used to get a User object directly from the User's
        folder acl_users, without wrapping it with group information.

        This is useful for UserFolders that define additional User classes,
        when you want to call specific methods on these user objects.

        For example, LDAPUserFolder defines a 'getProperty' method that's
        not inherited from the standard User object. You can, then, use
        the getUnwrappedUser() to get the matching user and call this
        method.
        """
        return self.Users.acl_users.getUser(name)


    def getUnwrappedGroup(self, name):
        """
        getUnwrappedGroup(self, name) => user object or None

        Same as getUnwrappedUser but for groups.
        """
        return self.Groups.acl_users.getUser(name)

    


    # ------------------------
    # Group-specific operation
    # ------------------------

    def getGroupNames(self, without_prefix = 0):
        """
        Fetch the list from GRUFGroups.
        """
        if not "acl_users" in self.Groups.objectIds():
            return ()
        return self.Groups.listGroups(without_prefix = without_prefix)

    def getGroups(self):
        """Return a list of user objects"""
        ret = []
        for n in self.getGroupNames():
            ret.append(self.getGroup(n))
        return filter(None, ret)                        
        # This prevents 'None' user objects to be returned. 
        # This happens for example with LDAPUserFolder when a LDAP 
        # query fetches too much records.


    def getGroup(self, name, prefixed = 1):
        """Return the named user object or None"""
        # Performance tricks
        if not name:
            return None
        
        # Unprefix group name
        if prefixed:
            newname = name[_group_prefix_len:]
            if not newname:
                return None
            if name[:_group_prefix_len] != GRUFFolder.GRUFGroups._group_prefix:
                return None
            name = newname

        # Fetch group
        u = self.Groups.acl_users.getUser(name)
        if u:
            return GRUFUser.GRUFUser(u, self, isGroup = 1).__of__(self)
            # $$$ check security for this !

        # If still not found, well... we cannot do anything else.
        Log(LOG_WARNING, "Didn't find group", name)
        return None


    # ------------------------
    # Group-specific operation
    # ------------------------

    def getPureUserNames(self, ):
        """
        Fetch the list of actual users from GRUFUsers.
        """
        if not "acl_users" in self.Users.objectIds():
            return ()
        ret = self.Users.acl_users.getUserNames()
        return ret


    def getPureUsers(self):
        """Return a list of pure user objects"""
        ret = []
        for n in self.getPureUserNames():
            ret.append(self.getUser(n))
        return filter(None, ret)                        
        # This prevents 'None' user objects to be returned. 
        # This happens for example with LDAPUserFolder when a 
        # LDAP query fetches too much records.


    # ------------------------
    # Authentication interface
    # ------------------------


    def authenticate(self, name, password, request):
        """
        Pass the request along to the underlying user-related UserFolder 
        object
        THIS METHOD RETURNS A USER OBJECT OR NONE, according to the code 
        in AccessControl/User.py
        """
        if "acl_users" in self.Users.objectIds():
            u = self.Users.acl_users.authenticate(name, password, request)
            if u:
                return GRUFUser.GRUFUser(u, self,).__of__(self)         
                # $$$ Check security for this !
            return None                                                 
            # The user cannot be authenticated => we return None

        # No acl_users in the Users folder => we refuse authentication
        return None
    
##    ## I DON'T KNOW IF WE HAVE TO PASS VALIDATE
##    def validate(self, request, auth='', roles=_noroles):
##        return self.Users.validate(request, auth, roles)


    # -----------------------------
    # Private User Folder interface
    # -----------------------------

    def _doAddUser(self, name, password, roles, domains, **kw):
        """Create a new user. This should be implemented by subclasses to
           do the actual adding of a user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        return self.Users.acl_users._doAddUser(name, password, 
                                               roles, domains, **kw)

    def _doChangeUser(self, name, password, roles, domains, **kw):
        """Modify an existing user. This should be implemented by subclasses
           to make the actual changes to a user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""
        return self.Users.acl_users._doChangeUser(name, password, 
                                                  roles, domains, **kw)

    def _doDelUsers(self, names):
        """Delete one or more users. This should be implemented by subclasses
           to do the actual deleting of users."""
        return self.Users.acl_users._doDelUsers(names)

   
InitializeClass(GroupUserFolder) 


