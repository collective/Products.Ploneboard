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
from AccessControl import Permissions
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


def manage_addGroupUserFolder(self, dtself=None, REQUEST=None, **ignored):
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

    security = ClassSecurityInfo()

    manage_options=( OFS.ObjectManager.ObjectManager.manage_options + \
        ( {'label':'Overview', 'action':'manage_overview'},
          {'label':'Audit', 'action':'manage_audit'},
          ) + \
        RoleManager.manage_options + \
        Item.manage_options )

    manage_main = OFS.ObjectManager.ObjectManager.manage_main
    manage_overview = DTMLFile('dtml/GroupUserFolder_overview', globals())
    manage_addUser = DTMLFile('dtml/addUser', globals())
    manage_audit = Products.PageTemplates.PageTemplateFile.PageTemplateFile('dtml/GRUF_audit', globals())

    __ac_permissions__=(
        ('Manage users',
         ('manage_users',
          'getUserById', 'user_names', 'setDomainAuthenticationMode',
          'userFolderAddUser', 'userFolderEditUser', 'userFolderDelUsers',
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


    security.declarePrivate('_post_init')
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

    security.declarePublic('getGroupPrefix')
    def getGroupPrefix(self):
        """ group prefix """
        return GRUFFolder.GRUFGroups._group_prefix

    security.declareProtected(Permissions.change_permissions, "getLocalRolesForDisplay")
    def getLocalRolesForDisplay(self, object):
        ## This is used for plone's local roles display
        ## This method returns a tuple (massagedUsername, roles, userType, actualUserName)
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
            result.append((massagedUsername, roles, userType, username))
        return tuple(result)    

    security.declarePrivate('getGRUFPhysicalRoot')
    def getGRUFPhysicalRoot(self,):
        # $$$ trick meant to be used within 
        # fake_getPhysicalRoot (see __init__)
        return self.getPhysicalRoot()   

    security.declareProtected(Permissions.view, 'getGRUFId')
    def getGRUFId(self,):
        """
        Alias to self.getId()
        """
        return self.getId()
    
    # ----------------------------------
    # Public UserFolder object interface
    # ----------------------------------

    security.declareProtected(Permissions.manage_users, "getUserNames")
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

    security.declareProtected(Permissions.manage_users, "getUsers")
    def getUsers(self):
        """Return a list of user objects"""
        ret = []
        for n in self.getUserNames():
            ret.append(self.getUser(n))

        return filter(None, ret)
        # This prevents 'None' user objects to be returned. 
        # This happens for example with LDAPUserFolder when a 
        # LDAP query fetches too much records.

    security.declareProtected(Permissions.manage_users, "getUser")
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
            ret = GRUFUser.GRUFUser(u, self,).__of__(self)
            Log(LOG_DEBUG, ret.aq_parent)
            return ret
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

    security.declareProtected(Permissions.manage_users, "getUnwrappedUser")
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

    security.declareProtected(Permissions.manage_users, "getUnwrappedGroup")
    def getUnwrappedGroup(self, name):
        """
        getUnwrappedGroup(self, name) => user object or None

        Same as getUnwrappedUser but for groups.
        """
        return self.Groups.acl_users.getUser(name)

    # ------------------------
    # Group-specific operation
    # ------------------------

    security.declareProtected(Permissions.manage_users, "getGroupNames")
    def getGroupNames(self, prefixed = 1):
        """
        Fetch the list from GRUFGroups.
        """
        if not "acl_users" in self.Groups.objectIds():
            return ()
        return self.Groups.listGroups(prefixed = prefixed)

    security.declareProtected(Permissions.manage_users, "getGroups")
    def getGroups(self):
        """Return a list of user objects"""
        ret = []
        for n in self.getGroupNames():
            ret.append(self.getGroup(n))
        return filter(None, ret)                        
        # This prevents 'None' user objects to be returned. 
        # This happens for example with LDAPUserFolder when a LDAP 
        # query fetches too much records.

    security.declareProtected(Permissions.manage_users, "getGroup")
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
        Log(LOG_DEBUG, "Didn't find group", name)
        return None


    # ------------------------
    # Group-specific operation
    # ------------------------

    security.declareProtected(Permissions.manage_users, "getPureUserNames")
    def getPureUserNames(self, ):
        """
        Fetch the list of actual users from GRUFUsers.
        """
        if not "acl_users" in self.Users.objectIds():
            return ()
        ret = self.Users.acl_users.getUserNames()
        return ret

    security.declareProtected(Permissions.manage_users, "getPureUsers")
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

    security.declarePrivate("authenticate")
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

    security.declarePrivate("_doAddUser")
    def _doAddUser(self, name, password, roles, domains, groups = (), **kw):
        """Create a new user. This should be implemented by subclasses to
           do the actual adding of a user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        # Prepare groups
        prefix = GRUFFolder.GRUFGroups._group_prefix
        roles = list(roles)
        gruf_groups = self.getGroupNames()
        for group in groups:
            if not group.startswith(prefix):
                group = "%s%s" % (prefix, group, )
            if not group in gruf_groups:
                raise ValueError, "Invalid group: '%s'" % (group, )
            roles.append(group)

        # Really add users
        return self.Users.acl_users._doAddUser(
            name,
            password, 
            roles,
            domains,
            **kw)

    security.declarePrivate("_doChangeUser")
    def _doChangeUser(self, name, password, roles, domains, **kw):
        """Modify an existing user. This should be implemented by subclasses
           to make the actual changes to a user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""
        return self.Users.acl_users._doChangeUser(name, password, 
                                                  roles, domains, **kw)

    security.declarePrivate("_doDelUsers")
    def _doDelUsers(self, names):
        """Delete one or more users. This should be implemented by subclasses
           to do the actual deleting of users."""
        return self.Users.acl_users._doDelUsers(names)


    #                                   #
    #           Groups interface        #
    #                                   #

    security.declarePrivate("_doAddGroup")
    def _doAddGroup(self, name, roles, **kw):
        """Create a new group. Password will be randomly created, and domain will be none"""

        domains = ()
        password = ""
        for x in range(0, 10):  # Password will be 10 chars long
            password = "%s%s" % (password, random.choice(string.lowercase), )
        return self.Groups.acl_users._doAddUser(
            name, password, roles, domains, **kw
            )

    security.declarePrivate("_doChangeGroup")
    def _doChangeGroup(self, name, roles, **kw):
        """Modify an existing group."""
        domains = ""
        password = ""
        for x in range(0, 10):  # Password will be 10 chars long
            password = "%s%s" % (password, random.choice(string.lowercase), )
        return self.Groups.acl_users._doChangeUser(name, password, 
                                                  roles, domains, **kw)

    security.declarePrivate("_doDelGroup")
    def _doDelGroup(self, names):
        """Delete one or more users. This should be implemented by subclasses
           to do the actual deleting of users."""
        return self.Groups.acl_users._doDelUsers(names)




    # ----------------------
    # Security audit methods
    # ----------------------

    security.declareProtected(Permissions.manage_users, "computeSecuritySettings")
    def computeSecuritySettings(self, folders, actors, permissions, cache = {}):
        """
        computeSecuritySettings(self, folders, actors, permissions, cache = {}) => return a structure that is suitable for security audit Page Template.

        - folders is the structure returned by getSiteTree()
        - actors is the structure returned by listUsersAndRoles()
        - permissions is ((id: permission), (id: permission), ...)
        - cache is passed along requests to make computing faster
        """
        # Scan folders and actors to get the relevant information
        usr_cache = {}
        for id, depth, path in folders:
            folder = self.unrestrictedTraverse(path)
            for kind, actor in actors:
                if kind in ("user", "group"):
                    # Init structure
                    if not cache.has_key(path):
                        cache[path] = {(kind, actor): {}}
                    elif not cache[path].has_key((kind, actor)):
                        cache[path][(kind, actor)] = {}
                    else:
                        cache[path][(kind, actor)] = {}

                    # Split kind into groups and get individual role information
                    perm_keys = []
                    usr = usr_cache.get(actor)
                    if not usr:
                        usr = self.getUser(actor)
                        usr_cache[actor] = usr
                    roles = usr.getRolesInContext(folder,)
                    for role in roles:
                        for perm_key in self.computeSetting(path, folder, role, permissions, cache).keys():
                            cache[path][(kind, actor)][perm_key] = 1
                        
                else:
                    # Get role information
                    self.computeSetting(path, folder, actor, permissions, cache)

        # Return the computed cache
        return cache


    security.declareProtected(Permissions.manage_users, "computeSetting")
    def computeSetting(self, path, folder, actor, permissions, cache):
        """
        computeSetting(......) => used by computeSecuritySettings to populate the cache for ROLES
        """
        # Avoid doing things twice
        kind = "role"
        if cache.get(path, {}).get((kind, actor), None) is not None:
##            Log(LOG_DEBUG, "**** Returning from the cache ****")
            return cache[path][(kind, actor)]

        # Initilize cache structure
        Log(LOG_DEBUG, "computeSetting", path, actor, )
        if not cache.has_key(path):
            cache[path] = {(kind, actor): {}}
        elif not cache[path].has_key((kind, actor)):
            cache[path][(kind, actor)] = {}

        # Analyze permission settings
        ps = folder.permission_settings()
        for perm_key, permission in permissions:
            # Check acquisition of permission setting.
            can = 0
            acquired = 0
            for p in ps:
                if p['name'] == permission:
                    acquired = not not p['acquire']

            # If acquired, call the parent recursively
            if acquired:
                parent = folder.aq_parent.getPhysicalPath()
                perms = self.computeSetting(parent, self.unrestrictedTraverse(parent), actor, permissions, cache)
                can = perms.get(perm_key, None)

            # Else, check permission here
            else:
                for p in folder.rolesOfPermission(permission):
                    if p['name'] == "Anonymous":
                        # If anonymous is allowed, then everyone is allowed
                        if p['selected']:
                            can = 1
                            break
                    if p['name'] == actor:
                        if p['selected']:
                            can = 1
                            break

            # Extend the data structure according to 'can' setting
            if can:
                cache[path][(kind, actor)][perm_key] = 1

        Log(LOG_DEBUG, "Returning", cache[path][(kind, actor)])
        return cache[path][(kind, actor)]

    security.declareProtected(Permissions.manage_users, "listUsersAndRoles")
    def listUsersAndRoles(self,):
        """
        listUsersAndRoles(self,) => list of tuples

        This method is used by the Security Audit page.
        """
        request = self.REQUEST
        display_roles = request.get('display_roles', 0)
        display_groups = request.get('display_groups', 0)
        display_users = request.get('display_users', 0)
        
        ret = []

        # Collect roles
        if display_roles:
            for r in self.aq_parent.valid_roles():
                ret.append(('role', r))

        # Collect users
        for u in self.getUserNames():
            obj = self.getUser(u)
            if hasattr(obj, 'isGroup'):
                if obj.isGroup():
                    if display_groups:
                        ret.append(('group', u))
                        continue

            if display_users:
                ret.append(('user', u))

        # Return list
        return ret

    security.declareProtected(Permissions.manage_users, "getSiteTree")
    def getSiteTree(self, obj=None, depth=0):
        """
        getSiteTree(self, obj=None, depth=0) => special structure
        
        This is used by the security audit page
        """
        ret = []
        if not obj:
            obj = self.aq_parent

        ret.append([obj.getId(), depth, string.join(obj.getPhysicalPath(), '/')])
        for sub in obj.objectValues():
            try:
                # Ignore user folders
                if sub.getId() in ('acl_users', ):
                    continue
                
                # Ignore portal_* stuff
                if sub.getId()[:len('portal_')] == 'portal_':
                    continue
                
                if sub.isPrincipiaFolderish:
                    ret.extend(self.getSiteTree(sub, depth + 1))

            except:
                # We ignore exceptions
                pass

        return ret

    security.declareProtected(Permissions.manage_users, "listAuditPermissions")
    def listAuditPermissions(self,):
        """
        listAuditPermissions(self,) => return a list of eligible permissions
        """
        ps = self.permission_settings()
        return map(lambda p: p['name'], ps)

    security.declareProtected(Permissions.manage_users, "getDefaultPermissions")
    def getDefaultPermissions(self,):
        """
        getDefaultPermissions(self,) => return default R & W permissions for security audit.
        """
        # If there's a Plone site in the above folder, use plonish permissions
        hasPlone = 0
        p = self.aq_parent
        Log(LOG_DEBUG, "p", p.meta_type)
        if p.meta_type == "CMF Site":
            hasPlone = 1
        else:
            for obj in p.objectValues():
                Log(LOG_DEBUG, "obj", obj.meta_type)
                if obj.meta_type == "CMF Site":
                    hasPlone = 1
                    break

        if hasPlone:
            return {'R': 'View',
                    'W': 'Modify portal content',
                    }
        else:
            return {'R': 'View',
                    'W': 'Change Images and Files',
                    }



   
InitializeClass(GroupUserFolder) 


