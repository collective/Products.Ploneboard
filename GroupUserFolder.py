##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL - All rights reserved
#
# This software is subject to the provisions of the GNU Public License,
# Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
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
from Products.PageTemplates import PageTemplateFile
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
from Products.PageTemplates import PageTemplateFile

DEBUG=1
#import zLOG
#
#def log(message,summary='',severity=0):
#    zLOG.LOG('GroupUserFolder: ',severity,summary,message)


_group_prefix_len = len(GRUFFolder.GRUFGroups._group_prefix)
_group_prefix = GRUFFolder.GRUFGroups._group_prefix

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


# ...this is used for direct user access...
# superGetAttr is assigned to whatever ObjectManager.__getattr__
# used to do.
try:
    superGetAttr = ObjectManager.__getattr__
except:
    try:
        superGetAttr = ObjectManager.inheritedAttribute('__getattr__')
    except:
        superGetAttr = None




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

    manage_options=( 
        (
        {'label':'Sources', 'action':'manage_GRUFContents'},
        {'label':'Overview', 'action':'manage_overview'},
        {'label':'Groups', 'action':'manage_groups'},
        {'label':'Users', 'action':'manage_users'},
        {'label':'Audit', 'action':'manage_audit'},
        ) + \
        OFS.ObjectManager.ObjectManager.manage_options + \
        RoleManager.manage_options + \
        Item.manage_options )

    manage_main = OFS.ObjectManager.ObjectManager.manage_main
    manage_overview = DTMLFile('dtml/GRUF_overview', globals())
    manage_addUser = DTMLFile('dtml/addUser', globals())
    manage_audit = PageTemplateFile.PageTemplateFile('dtml/GRUF_audit', globals())
    manage_groups = PageTemplateFile.PageTemplateFile('dtml/GRUF_groups', globals())
    manage_users = PageTemplateFile.PageTemplateFile('dtml/GRUF_users', globals())
    manage_newusers = PageTemplateFile.PageTemplateFile('dtml/GRUF_newusers', globals())
    manage_GRUFContents = PageTemplateFile.PageTemplateFile('dtml/GRUF_contents', globals())
    manage_user = PageTemplateFile.PageTemplateFile('dtml/GRUF_user', globals())

    __ac_permissions__=(
        ('Manage users',
         ('manage_users',
          'getUserById', 'user_names', 'setDomainAuthenticationMode',
          'userFolderAddUser', 'userFolderEditUser', 'userFolderDelUsers',
          )
         ),
        )


    # Color constants, only useful within GRUF management screens
    user_color = "#006600"
    group_color = "#000099"
    role_color = "#660000"
    

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

    # XXX This method has NOT to be public !!! It is because of a CMF inconsistancy.
    # folder_localrole_form is accessible to users who have the manage_properties permissions
    # (according to portal_types/Folder/Actions information). This is silly !
    # folder_localrole_form should be, in CMF, accessible only to those who have the
    # manage_users permissions instead of manage_properties permissions.
    # This is yet another one CMF bug we have to care about.
    security.declarePublic("getLocalRolesForDisplay")
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
            ret = GRUFUser.GRUFUser(u, self,).__of__(self)
            return ret
            # $$$ Check security for this !
        
        # If not found, fetch groups (then the user must be 
        # prefixed by 'group_' prefix)

        u = self.Groups.getGroup(name)
        if u:
            # We changed that because the previous code returned
            # a double-wrapped group object...
            return u
 
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
        """Return a list of user-like objects belonging to groups"""
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
            ret = GRUFUser.GRUFUser(u, self, isGroup = 1).__of__(self)
            return ret
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
    def _doChangeUser(self, name, password, roles, domains, groups = (), **kw):
        """
        Modify an existing user. This should be implemented by subclasses
        to make the actual changes to a user. The 'password' will be the
        original input password, unencrypted. The implementation of this
        method is responsible for performing any needed encryption.
        
        A None password should not change it (well, we hope so)
        """
        roles = list(roles)
        groups = list(groups)
        
        # Change groups affectation
        cur_groups = self.getGroups()
        given_roles = tuple(self.getUser(name).getRoles()) + tuple(roles)
        for group in groups:
            if not group.startswith(_group_prefix, ):
                group = "%s%s" % (_group_prefix, group, )
            if not group in cur_groups and not group in given_roles:
                roles.append(group)

        # Change the user itself
        return self.Users.acl_users._doChangeUser(name, password, 
                                                  roles, domains, **kw)

    security.declarePrivate("_updateUser")
    def _updateUser(self, name, password = None, roles = None, domains = None, groups = None):
        """
        _updateUser(self, name, password = None, roles = None, domains = None, groups = None)
        
        Front-end to _doChangeUser, but with a better default value support.
        We guarantee that None values will let the underlying UF keep the original ones.
        This is not true for the password: some buggy UF implementation may not
        handle None password correctly :-(
        """
        # Get the former values if necessary. Username must be valid !
        usr = self.getUser(name)
        if roles is None:
            # Remove invalid roles and group names
            roles = usr._original_roles
            roles = filter(lambda x: not x.startswith(_group_prefix), roles)
            roles = filter(lambda x: x not in ('Anonymous', 'Authenticated', 'Shared'), roles)
        if domains is None:
            domains = usr._original_domains
        if groups is None:
            groups = usr.getGroups(no_recurse = 1)

        # Change the user
        return self._doChangeUser(name, password, roles, domains, groups)

    security.declarePrivate("_doDelUsers")
    def _doDelUsers(self, names):
        """Delete one or more users. This should be implemented by subclasses
           to do the actual deleting of users."""
        return self.Users.acl_users._doDelUsers(names)


    #                                   #
    #           Groups interface        #
    #                                   #

    security.declarePrivate("_doAddGroup")
    def _doAddGroup(self, name, roles, groups = (), **kw):
        """
        Create a new group. Password will be randomly created, and domain will be None.
        Supports nested groups.
        """
        # Prepare initial data
        domains = ()
        password = ""
        if roles is None:
            roles = []
        if groups is None:
            groups = []
        
        for x in range(0, 10):  # Password will be 10 chars long
            password = "%s%s" % (password, random.choice(string.lowercase), )

        # Compute roles
        roles = list(roles)
        prefix = GRUFFolder.GRUFGroups._group_prefix
        gruf_groups = self.getGroupNames()
        for group in groups:
            if not group.startswith(prefix):
                group = "%s%s" % (prefix, group, )
            if group == "%s%s" % (prefix, name, ):
                raise ValueError, "Infinite recursion for group '%s'." % (group, )
            if not group in gruf_groups:
                raise ValueError, "Invalid group: '%s'" % (group, )
            roles.append(group)

        # Actual creation
        return self.Groups.acl_users._doAddUser(
            name, password, roles, domains, **kw
            )

    security.declarePrivate("_doChangeGroup")
    def _doChangeGroup(self, name, roles, groups = (), **kw):
        """Modify an existing group."""
        roles = list(roles or [])
        groups = list(groups or [])

        # Remove prefix if given
        if name.startswith(self.getGroupPrefix()):
            name = name[_group_prefix_len:]

        # Check if group exists
        grp = self.getGroup(name, prefixed = 0)
        if grp is None:
            raise ValueError, "Invalid group: '%s'" % (name,)

        # Change groups affectation
        cur_groups = self.getGroups()
        given_roles = tuple(grp.getRoles()) + tuple(roles)
        for group in groups:
            if not group.startswith(_group_prefix, ):
                group = "%s%s" % (_group_prefix, group, )
            if group == "%s%s" % (_group_prefix, grp.id):
                raise ValueError, "Cannot affect group '%s' to itself!" % (name, )        # Prevent direct inclusion of self
            new_grp = self.getGroup(group)
            if not new_grp:
                raise ValueError, "Invalid or inexistant group: '%s'" % (group, )
            if "%s%s" % (_group_prefix, grp.id) in new_grp.getGroups():
                raise ValueError, "Cannot affect %s to group '%s' as it would lead to circular references." % (group, name, )        # Prevent indirect inclusion of self
            if not group in cur_groups and not group in given_roles:
                roles.append(group)

        # Perform the change
        domains = ""
        password = ""
        for x in range(0, 10):  # Password will be 10 chars long
            password = "%s%s" % (password, random.choice(string.lowercase), )
        return self.Groups.acl_users._doChangeUser(name, password, 
                                                  roles, domains, **kw)

    security.declarePrivate("_updateUser")
    def _updateGroup(self, name, roles = None, groups = None):
        """
        _updateUser(self, name, roles = None, groups = None)
        
        Front-end to _doChangeUser, but with a better default value support.
        We guarantee that None values will let the underlying UF keep the original ones.
        This is not true for the password: some buggy UF implementation may not
        handle None password correctly but we do not care for Groups.

        group name can be prefixed or not
        """
        # Remove prefix if given
        if name.startswith(self.getGroupPrefix()):
            name = name[_group_prefix_len:]

        # Get the former values if necessary. Username must be valid !
        usr = self.getGroup(name, prefixed = 0)
        if roles is None:
            # Remove invalid roles and group names
            roles = usr._original_roles
            roles = filter(lambda x: not x.startswith(_group_prefix), roles)
            roles = filter(lambda x: x not in ('Anonymous', 'Authenticated', 'Shared'), roles)
        if groups is None:
            groups = usr.getGroups(no_recurse = 1)

        # Change the user
        return self._doChangeGroup(name, roles, groups)


    security.declarePrivate("_doDelGroup")
    def _doDelGroup(self, name):
        """Delete one user."""
        # Remove prefix if given
        if name.startswith(self.getGroupPrefix()):
            name = name[_group_prefix_len:]

        # Delete it
        return self.Groups.acl_users._doDelUsers([name])

    security.declarePrivate("_doDelGroups")
    def _doDelGroups(self, names):
        """Delete one or more users."""
        for group in names:
            self._doDelGroup(group)



    #                                           #
    #      Pretty Management form methods       #
    #                                           #


    security.declarePublic('getGRUFVersion')
    def getGRUFVersion(self,):
        """
        getGRUFVersion(self,) => Return human-readable GRUF version as a string.
        """
        rev_date = "$Date: 2003/07/24 18:46:15 $"[7:-2]
        return "%s / Revised %s" % (version__, rev_date)
    

    reset_entry = "__None__"            # Special entry used for reset

    security.declareProtected(Permissions.manage_users, "changeUser")
    def changeUser(self, user, groups = [], roles = [], REQUEST = {}, ):
        """
        changeUser(self, user, groups = [], roles = [], REQUEST = {}, ) => used in ZMI
        """
        obj = self.getUser(user)
        if obj.isGroup():
            self._updateGroup(name = user, groups = groups, roles = roles, )
        else:
            self._updateUser(name = user, groups = groups, roles = roles, )


        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + "/" + user + "/manage_workspace")

    security.declareProtected(Permissions.manage_users, "deleteUser")
    def deleteUser(self, user, REQUEST = {}, ):
        """
        deleteUser(self, user, REQUEST = {}, ) => used in ZMI
        """
        pass
        

    security.declareProtected(Permissions.manage_users, "changeOrCreateUsers")
    def changeOrCreateUsers(self, users = [], groups = [], roles = [], new_users = [], REQUEST = {}, ):
        """
        changeOrCreateUsers => affect roles & groups to users and/or create new users
        
        All parameters are strings or lists (NOT tuples !).
        NO CHECKING IS DONE. This is an utility method !
        """
        # Manage roles / groups deletion
        del_roles = 0
        del_groups = 0
        if self.reset_entry in roles:
            roles.remove(self.reset_entry)
            del_roles = 1
        if self.reset_entry in groups:
            groups.remove(self.reset_entry)
            del_groups = 1
        if not roles and not del_roles:
            roles = None                # None instead of [] to avoid deletion
            add_roles = []
        else:
            add_roles = roles
        if not groups and not del_groups:
            groups = None
            add_groups = []
        else:
            add_groups = groups

        # Passwords management
        passwords_list = []
        
        # Create brand new users
        for new in new_users:
            # Strip name
            name = string.strip(new)
            if not name:
                continue

            # Avoid erasing former users
            if name in self.getUserNames():
                continue
            
            # Generate a random password
            password = ""
            for x in range(0, 8):  # Password will be 8 chars long
                password = "%s%s" % (password, random.choice("ABCDEFGHIJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"), )
            self._doAddUser(name, password, add_roles, (), add_groups, )

            # Store the newly created password
            passwords_list.append({'name':name, 'password':password})
        
        # Update existing users
        for user in users:
            self._updateUser(name = user, groups = groups, roles = roles, )

        # Redirect if no users have been created
        if not passwords_list:
            if REQUEST.has_key('RESPONSE'):
                return REQUEST.RESPONSE.redirect(self.absolute_url() + "/manage_users")

        # Show passwords form
        REQUEST.set('USER_PASSWORDS', passwords_list)
        return self.manage_newusers(None, self)


    security.declareProtected(Permissions.manage_users, "deleteUsers")
    def deleteUsers(self, users = [], REQUEST = {}):
        """
        deleteUsers => explicit
        
        All parameters are strings. NO CHECKING IS DONE. This is an utility method !
        """
        # Delete them
        self._doDelUsers(users, )

        # Redirect
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + "/manage_users")


    security.declareProtected(Permissions.manage_users, "changeOrCreateGroups")
    def changeOrCreateGroups(self, groups = [], roles = [], nested_groups = [], new_groups = [], REQUEST = {}, ):
        """
        changeOrCreateGroups => affect roles to groups and/or create new groups
        
        All parameters are strings. NO CHECKING IS DONE. This is an utility method !
        """
        # Manage roles / groups deletion
        del_roles = 0
        del_groups = 0
        if self.reset_entry in roles:
            roles.remove(self.reset_entry)
            del_roles = 1
        if self.reset_entry in nested_groups:
            nested_groups.remove(self.reset_entry)
            del_groups = 1
        if not roles and not del_roles:
            roles = None                # None instead of [] to avoid deletion
            add_roles = []
        else:
            add_roles = roles
        if not nested_groups and not del_groups:
            nested_groups = None
            add_groups = []
        else:
            add_groups = nested_groups

        # Create brand new groups
        for new in new_groups:
            name = string.strip(new)
            if not name:
                continue
            self._doAddGroup(name, roles, groups = add_groups)
        
        # Update existing groups
        for group in groups:
            self._updateGroup(group, roles = roles, groups = nested_groups)

        # Redirect
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + "/manage_groups")


    security.declareProtected(Permissions.manage_users, "deleteGroups")
    def deleteGroups(self, groups = [], REQUEST = {}):
        """
        deleteGroups => explicit
        
        All parameters are strings. NO CHECKING IS DONE. This is an utility method !
        """
        # Delete groups
        for group in groups:
            self._doDelGroup(group, )

        # Redirect
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + "/manage_groups")



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
            for kind, actor, display, handle, html in actors:
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
            return cache[path][(kind, actor)]

        # Initilize cache structure
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

        return cache[path][(kind, actor)]


    security.declarePrivate('_getNextHandle')
    def _getNextHandle(self, index):
        """
        _getNextHandle(self, index) => utility function to
        get an unique handle for each legend item.
        """
        return "%02d" % index
            

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

        role_index = 0
        user_index = 0
        group_index = 0
        ret = []

        # Collect roles
        if display_roles:
            for r in self.aq_parent.valid_roles():
                handle = "R%02d" % role_index
                role_index += 1
                ret.append(('role', r, r, handle, r))

        # Collect users
        for u in self.getUserNames():
            obj = self.getUser(u)
            if hasattr(obj, 'isGroup'):
                if obj.isGroup():
                    if display_groups:
                        handle = "G%02d" % group_index
                        html = obj.asHTML()
                        group_index += 1
                        ret.append(('group', u, obj.getUserNameWithoutGroupPrefix(), handle, html))
                        continue

            if display_users:
                html = obj.asHTML()
                handle = "U%02d" % user_index
                user_index += 1
                ret.append(('user', u, u, handle, html))

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
        if p.meta_type == "CMF Site":
            hasPlone = 1
        else:
            for obj in p.objectValues():
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


    #                                                                           #
    #                           Users/Groups tree view                          #
    #                                (ZMI only)                                 #
    #                                                                           #


    security.declarePrivate('getTreeInfo')
    def getTreeInfo(self, usr, dict = {}):
        "utility method"
        # Prevend infinite recursions
        name = usr.getUserName()
        if dict.has_key(name):
            return
        dict[name] = {}

        # Properties
        noprefix = usr.getUserNameWithoutGroupPrefix()
        is_group = usr.isGroup()
        if usr.isGroup():
            icon = self.Groups.icon
        else:
            icon = self.Users.icon

        # Subobjects
        belongs_to = []
        for grp in usr.getGroups(no_recurse = 1):
            belongs_to.append(grp)
            self.getTreeInfo(self.getGroup(grp))

        # Append (and return) structure
        dict[name] = {
            "name": noprefix,
            "is_group": is_group,
            "icon": icon,
            "belongs_to": belongs_to,
            }
        return dict

        
    security.declarePrivate("tpValues")
    def tpValues(self):
        # Avoid returning HUUUUUUGE lists
        ngroups = len(self.getGroupNames())
        nusers = len(self.getUserNames())
        if ngroups + nusers <= MAX_TREE_USERS_AND_GROUPS:
            meth_list = self.getUsers
        elif ngroups <= MAX_TREE_USERS_AND_GROUPS:
            meth_list = self.getGroups
        else:
            return []

        # Get top-level user and groups list
        tree_dict = {}
        top_level_names = []
        top_level = []
        for usr in meth_list():
            self.getTreeInfo(usr, tree_dict)
            if not usr.getGroups(no_recurse = 1):
                top_level_names.append(usr.getUserName())
        for id in top_level_names:
            top_level.append(treeWrapper(id, tree_dict))

        # Return this top-level list
        top_level.sort(lambda x, y: cmp(x.sortId(), y.sortId()))
        return top_level
        

    def tpId(self,):
        return self.getId()


    #                                                                           #
    #                      Direct traversal to user or group info               #
    #                                                                           #

    def manage_workspace(self, REQUEST):
        """
        manage_workspace(self, REQUEST) => Overrided to allow direct user or group traversal
        via the left tree view.
        """
        path = string.split(REQUEST.PATH_INFO, '/')[:-1]
        username = path[-1]
        if username in self.getUserNames():
            REQUEST.set('username', username)
            REQUEST.set('MANAGE_TABS_NO_BANNER', '1')   # Prevent use of the manage banner
            return self.restrictedTraverse('manage_user')()
        else:
            # Default management screen
            return self.restrictedTraverse('manage_GRUFContents')()


    def __getattr__(self, name):
        '''
        Looks for the name of a user or a group.
        '''
        if name in self.getUserNames():
            return self.restrictedTraverse('')

        if superGetAttr is None:
            raise AttributeError, name
        return superGetAttr(self, name)

   
class treeWrapper:
    """
    treeWrapper: Wrapper around user/group objects for the tree
    """
    def __init__(self, id, tree, parents = []):
        """
        __init__(self, id, tree, parents = []) => wraps the user object for dtml-tree
        """
        # Prepare self-contained information
        self._id = id
        self.name = tree[id]['name']
        self.icon = tree[id]['icon']
        self.is_group = tree[id]['is_group']
        parents.append(id)
        self.path = parents

        # Prepare subobjects information
        subobjects = []
        for grp_id in tree.keys():
            if id in tree[grp_id]['belongs_to']:
                subobjects.append(treeWrapper(grp_id, tree, parents))
        subobjects.sort(lambda x, y: cmp(x.sortId(), y.sortId()))
        self.subobjects = subobjects

    def id(self,):
        return self.name

    def sortId(self,):
        if self.is_group:
            return "__%s" % (self._id,)
        else:
            return self._id

    def tpValues(self,):
        """
        Return 'subobjects'
        """
        return self.subobjects

    def tpId(self,):
        return self._id

    def tpURL(self,):
        return self.tpId()

InitializeClass(GroupUserFolder) 


