##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL - All rights reserved
#
##############################################################################

"""GroupUserFolder product"""

# fakes a method from a DTML file
from Globals import MessageDialog, DTMLFile

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Globals import InitializeClass
from Acquisition import aq_base, aq_inner, aq_parent
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
import sys
import time
import math
import random
from global_symbols import *
import AccessControl.User
import GRUFFolder
import GRUFUser
from Products.PageTemplates import PageTemplateFile
import class_utility

from interfaces.IUserFolder import IUserFolder
 
## Developers notes
##
## The REQUEST.GRUF_PROBLEM variable is defined whenever GRUF encounters
## a problem than can be showed in the management screens. It's always
## logged as LOG_WARNING level anyway.

_marker = []

def unique(sequence, _list = 0):
    """Make a sequence a list of unique items"""
    uniquedict = {}
    for v in sequence:
        uniquedict[v] = 1
    if _list:
        return list(uniquedict.keys())
    return tuple(uniquedict.keys())


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
                      AccessControl.User.BasicUserFolder,
                      ):
    """
    GroupUserFolder => User folder with groups management
    """

    #                                                                           #
    #                              ZOPE  INFORMATION                            #
    #                                                                           #
    
    meta_type='Group User Folder'
    id       ='acl_users'
    title    ='Group-aware User Folder'

    __implements__ = (IUserFolder, )

    isAnObjectManager = 1
    isPrincipiaFolderish = 1
    isAUserFolder = 1

##    _haveLDAPUF = 0

    security = ClassSecurityInfo()

    manage_options=(
        (
        {'label':'Overview', 'action':'manage_overview'},
        {'label':'Sources', 'action':'manage_GRUFSources'},
        {'label':'Groups', 'action':'manage_groups'},
        {'label':'Users', 'action':'manage_users'},
        {'label':'Audit', 'action':'manage_audit'},
        ) + \
        OFS.ObjectManager.ObjectManager.manage_options + \
        RoleManager.manage_options + \
        Item.manage_options )

    manage_main = OFS.ObjectManager.ObjectManager.manage_main
##    manage_overview = DTMLFile('dtml/GRUF_overview', globals())
    manage_overview = PageTemplateFile.PageTemplateFile('dtml/GRUF_overview', globals())
    manage_audit = PageTemplateFile.PageTemplateFile('dtml/GRUF_audit', globals())
    manage_groups = PageTemplateFile.PageTemplateFile('dtml/GRUF_groups', globals())
    manage_users = PageTemplateFile.PageTemplateFile('dtml/GRUF_users', globals())
    manage_newusers = PageTemplateFile.PageTemplateFile('dtml/GRUF_newusers', globals())
    manage_GRUFSources = PageTemplateFile.PageTemplateFile('dtml/GRUF_contents', globals())
    manage_user = PageTemplateFile.PageTemplateFile('dtml/GRUF_user', globals())

    __ac_permissions__=(
        ('Manage users',
         ('manage_users',
          'user_names', 'setDomainAuthenticationMode',
          )
         ),
        )


    # Color constants, only useful within GRUF management screens
    user_color = "#006600"
    group_color = "#000099"
    role_color = "#660000"

    # User and group images
    img_user = ImageFile.ImageFile('www/GRUFUsers.gif', globals())
    img_group = ImageFile.ImageFile('www/GRUFGroups.gif', globals())



    #                                                                           #
    #                             OFFICIAL INTERFACE                            #
    #                                                                           #
    
    security.declareProtected(Permissions.manage_users, "getUserNames")
    def getUserNames(self, __include_groups__ = 1, __include_users__ = 1, __groups_prefixed__ = 0):
        """
        Return a list of all possible user atom names in the system.
        Groups will be returned WITHOUT their prefix by this method.
        So, there might be a collision between a user name and a group name.
        [NOTA: This method is time-expensive !]
        """
##        if __include_users__:
##            LogCallStack(LOG_DEBUG, "This call can be VERY expensive!")
        names = []
        ldap_sources = []

        # Fetch users in user sources
        if __include_users__:
            for src in self.listUserSources():
                names.extend(src.getUserNames())

        # Append groups if possible
        if __include_groups__:
            # Regular groups
            if "acl_users" in self._getOb('Groups').objectIds():
                names.extend(self.Groups.listGroups(prefixed = __groups_prefixed__))

            # LDAP groups
            for ldapuf in ldap_sources:
                if ldapuf._local_groups:
                    continue
                for g in ldapuf.getGroups(attr = LDAP_GROUP_RDN):
                    if __groups_prefixed__:
                        names.append("%s%s" % (GROUP_PREFIX, g))
                    else:
                        names.append(g)
        # Return a list of unique names
        return unique(names, _list = 1)

    security.declareProtected(Permissions.manage_users, "getUserIds")
    def getUserIds(self,):
        """
        Return a list of all possible user atom ids in the system.
        WARNING: Please see the id Vs. name consideration at the
        top of this document. So, groups will be returned
        WITH their prefix by this method
        [NOTA: This method is time-expensive !]
        """
        return self.getUserNames(__groups_prefixed__ = 1)
    

    security.declareProtected(Permissions.manage_users, "getUsers")
    def getUsers(self, __include_groups__ = 1, __include_users__ = 1):
        """Return a list of user and group objects.
        In case of some UF implementations, the returned object may only be a subset
        of all possible users.
        In other words, you CANNOT assert that len(getUsers()) equals len(getUserNames()).
        With cache-support UserFolders, such as LDAPUserFolder, the getUser() method will
        return only cached user objects instead of fetching all possible users.
        """
        ret = []
        names = []

        # Fetch groups first (then the user must be
        # prefixed by 'group_' prefix)
        if __include_groups__:
##            # Fetch LDAP groups
##            if self._haveLDAPUF:
##                for src in self.listUserSources():
##                    if not hasattr(src, LDAPUF_METHOD):                # We check if we have an LDAPUF
##                        continue

##                    # Scan LDAP groups
##                    if src._local_groups:
##                        continue
##                    for group in src.getGroups(attr = LDAP_GROUP_RDN):
##                        # Create a dummy user
##                        u = AccessControl.User.SimpleUser(group, '', [], [])

##                        # Bind it to a gruf user
##                        ret.append(GRUFUser.GRUFLDAPGroup(
##                            self, u, isGroup = 1, source_id = "Groups"
##                            ).__of__(self))


            # Fetch regular groups
            for u in self._getOb('Groups').acl_users.getUsers():
                if not u:
                    continue        # Ignore empty users

                name = u.getId()
                if name in names:
                    continue        # Prevent double users inclusion

                # Append group
                names.append(name)
                ret.append(
                    GRUFUser.GRUFGroup(u, self, isGroup = 1, source_id = "Groups").__of__(self)
                    )


        # Fetch users then
        if __include_users__:
            for src in self.listUserSources():
                for u in src.getUsers():
                    if not u:
                        continue        # Ignore empty users

                    name = u.getId()
                    if name in names:
                        continue        # Prevent double users inclusion

                    # Append user
                    names.append(name)
                    ret.append(
                        GRUFUser.GRUFUser(u, self, source_id = src.getUserSourceId(), isGroup = 0).__of__(self)
                        )

        return ret

    security.declareProtected(Permissions.manage_users, "getUser")
    def getUser(self, name, __include_users__ = 1, __include_groups__ = 1, __force_group_id__ = 0):
        """
        Return the named user object or None.
        User have precedence over group.

        XXX Have to improve perfs here
        """
        # Prevent infinite recursion when instanciating a GRUF
        # without having sub-acl_users set
        if not "acl_users" in self._getOb('Groups').objectIds():
            return None
        
        # Fetch groups first (then the user must be prefixed by 'group_' prefix)
        if __include_groups__ and name.startswith(GROUP_PREFIX):
            id = name[GROUP_PREFIX_LEN:]

            # Fetch regular groups
            u = self._getOb('Groups')._getGroup(id)
            if u:
                ret = GRUFUser.GRUFGroup(
                    u, self, isGroup = 1, source_id = "Groups"
                    ).__of__(self)
                return ret              # XXX This violates precedence
 
##            # Fetch LDAP groups
##            if self._haveLDAPUF:
##                for src in self.listUserSources():
##                    if not hasattr(src, LDAPUF_METHOD):                # We check if we have an LDAPUF
##                        continue
##                    if src._local_groups:
##                        continue
##                    groups = src.getGroups(attr = LDAP_GROUP_RDN)
##                    if id in groups:
##                        # Create a dummy user
##                        u = AccessControl.User.SimpleUser(name, '', [], [])

##                        # Bind it to a gruf user
##                        Log(LOG_DEBUG, "id", id, u, )
##                        return GRUFUser.GRUFLDAPGroup(
##                            u, self, isGroup = 1, source_id = "Groups"
##                            ).__of__(self)
                
        # Fetch users then
        if __include_users__:
            for src in self.listUserSources():
                u = src.getUser(name)
                if u:
                    ret = GRUFUser.GRUFUser(u, self, source_id = src.getUserSourceId(), isGroup = 0).__of__(self)
                    return ret

        # Then desperatly try to fetch groups (without beeing prefixed by 'group_' prefix)
        if __include_groups__ and (not __force_group_id__):
            u = self._getOb('Groups')._getGroup(name)
            if u:
                ret = GRUFUser.GRUFGroup(u, self, isGroup = 1, source_id = "Groups").__of__(self)
                return ret
 
        return None


    security.declareProtected(Permissions.manage_users, "getUserById")
    def getUserById(self, id, default=_marker):
        """Return the user atom corresponding to the given id. Can return groups.
        """
        ret = self.getUser(id, __force_group_id__ = 1)
        if not ret:
            if default is _marker:
                raise ValueError, "Invalid user or group id: '%s'" % (id, )
            ret = default
        return ret


    security.declareProtected(Permissions.manage_users, "getUserByName")
    def getUserByName(self, name, default=_marker):
        """Same as getUser() but works with a name instead of an id.
        [NOTA: Theorically, the id is a handle, while the name is the actual login name.
        But difference between a user id and a user name is unsignificant in
        all current User Folder implementations... except for GROUPS.]
        """
        # Try to fetch a user first
        usr = self.getUser(name)

        # If not found, try to fetch a group by appending the prefix
        if not usr:
            name = "%s%s" % (GROUP_PREFIX, name)
            usr = self.getUserById(name, default)

        return usr

    security.declareProtected(Permissions.manage_users, "getPureUserNames")
    def getPureUserNames(self, ):
        """Fetch the list of actual users from GRUFUsers.
        """
        return self.getUserNames(__include_groups__ = 0)


    security.declareProtected(Permissions.manage_users, "getPureUserIds")
    def getPureUserIds(self,):
        """Same as getUserIds() but without groups
        """
        return self.getUserNames(__include_groups__ = 0)

    security.declareProtected(Permissions.manage_users, "getPureUsers")
    def getPureUsers(self):
        """Return a list of pure user objects.
        """
        return self.getUsers(__include_groups__ = 0)

    security.declareProtected(Permissions.manage_users, "getPureUser")
    def getPureUser(self, id, ):
        """Return the named user object or None"""
        # Performance tricks
        if not id:
            return None
        
        # Fetch it
        return self.getUser(id, __include_groups__ = 0)


    security.declareProtected(Permissions.manage_users, "getGroupNames")
    def getGroupNames(self, ):
        """Same as getUserNames() but without pure users.
        """
        return self.getUserNames(__include_users__ = 0, __groups_prefixed__ = 0)

    security.declareProtected(Permissions.manage_users, "getGroupIds")
    def getGroupIds(self, ):
        """Same as getUserNames() but without pure users.
        """
        return self.getUserNames(__include_users__ = 0, __groups_prefixed__ = 1)

    security.declareProtected(Permissions.manage_users, "getGroups")
    def getGroups(self):
        """Same as getUsers() but without pure users.
        """
        return self.getUsers(__include_users__ = 0)

    security.declareProtected(Permissions.manage_users, "getGroup")
    def getGroup(self, name, prefixed = 1):
        """Return the named user object or None"""
        # Performance tricks
        if not name:
            return None

        # Unprefix group name
        if not name.startswith(GROUP_PREFIX):
            name = "%s%s" % (GROUP_PREFIX, name, )
            
        # Fetch it
        return self.getUser(name, __include_users__ = 0)

    security.declareProtected(Permissions.manage_users, "getGroupById")
    def getGroupById(self, id, default = _marker):
        """Same as getUserById(id) but forces returning a group.
        """
        ret = self.getUser(id, __include_users__ = 0, __force_group_id__ = 1)
        if not ret:
            if default is _marker:
                raise ValueError, "Invalid user: '%s'" % (id, )
            ret = default
        return ret

    security.declareProtected(Permissions.manage_users, "getGroupByName")
    def getGroupByName(self, name, default = _marker):
        """Same as getUserByName(name) but forces returning a group.
        """
        ret = self.getUser(name, __include_users__ = 0, __force_group_id__ = 0)
        if not ret:
            if default is _marker:
                raise ValueError, "Invalid user: '%s'" % (name, )
            ret = default
        return ret



    #                                                                           #
    #                              REGULAR MUTATORS                             #
    #                                                                           #

    security.declareProtected(Permissions.manage_users, "userFolderAddUser")
    def userFolderAddUser(self, name, password, roles = (), domains = (), groups = (), **kw):
        """API method for creating a new user object. Note that not all
        user folder implementations support dynamic creation of user
        objects.
        """
        return self._doAddUser(name, password, roles, domains, groups, **kw)
    
    security.declareProtected(Permissions.manage_users, "userFolderEditUser")
    def userFolderEditUser(self, name, password, roles, domains = (), groups = (), **kw):
        """API method for changing user object attributes. Note that not
        all user folder implementations support changing of user object
        attributes."""
        return self._doChangeUser(name, password, roles, domains, groups, **kw)

    security.declareProtected(Permissions.manage_users, "userFolderDelUsers")
    def userFolderDelUsers(self, names):
        """API method for deleting one or more user atom objects. Note that not
        all user folder implementations support deletion of user objects."""
        return self._doDelUsers(names)

    security.declareProtected(Permissions.manage_users, "userFolderAddGroup")
    def userFolderAddGroup(self, name, roles = (), groups = (), **kw):
        """API method for creating a new group.
        """
        while name.startswith(GROUP_PREFIX):
            name = name[GROUP_PREFIX_LEN:]
        return self._doAddGroup(name, roles, groups, **kw)
        
    security.declareProtected(Permissions.manage_users, "userFolderEditGroup")
    def userFolderEditGroup(self, name, roles, groups = (), **kw):
        """API method for changing group object attributes.
        """
        return self._doChangeGroup(name, roles, groups = groups, **kw)

    security.declareProtected(Permissions.manage_users, "userFolderDelGroups")
    def userFolderDelGroups(self, names):
        """API method for deleting one or more group objects.
        Implem. note : All ids must be prefixed with 'group_',
        so this method ends up beeing only a filter of non-prefixed ids
        before calling userFolderDelUsers().
        """
        return self._doDelGroups(names)



    #                                                                           #
    #                               SEARCH METHODS                              #
    #                                                                           #


    security.declareProtected(Permissions.manage_users, "searchUsersByAttribute")
    def searchUsersByAttribute(self, attribute, search_term):
        """Return user ids whose 'attribute' match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        This will return all users whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON USER FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF).
        'attribute' can be 'id' or 'name' for all UF kinds, or anything else for LDAPUF.
        """
        ret = []
        for src in self.listUserSources():
            # Use source-specific search methods if available
            if hasattr(src.aq_base, "findUser"):
                # LDAPUF
                id_attr = src._uid_attr
                if attribute == 'name':
                    attr = src._login_attr
                elif attribute == 'id':
                    attr = src._uid_attr
                else:
                    attr = attribute
                users = src.findUser(attr, search_term)
                ret.extend(
                    [ u[id_attr] for u in users ],
                    )
            else:
                # Other types of user folder
                search_term = search_term.lower()

                # Find the proper method according to the attribute type
                if attribute == "name":
                    method = "getName"
                elif attribute == "id":
                    method = "getId"
                else:
                    raise NotImplementedError, "Attribute searching is only supported for LDAPUserFolder by now."

                # Actually search
                for u in self.getUsers(__include_groups__ = 0):
                    s = getattr(u, method)().lower()
                    if string.find(s, search_term) != -1:
                        ret.append(u.getId())
        return ret

    security.declareProtected(Permissions.manage_users, "searchUsersByName")
    def searchUsersByName(self, search_term):
        """Return user ids whose name match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        This will return all users whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON USER FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF)
        """
        return self.searchUsersByAttribute("name", search_term)

    security.declareProtected(Permissions.manage_users, "searchUsersById")
    def searchUsersById(self, search_term):
        """Return user ids whose id match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        This will return all users whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON USER FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF)
        """
        return self.searchUsersByAttribute("id", search_term)


    security.declareProtected(Permissions.manage_users, "searchGroupsByAttribute")
    def searchGroupsByAttribute(self, attribute, search_term):
        """Return group ids whose 'attribute' match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying group folder:
        it may return all groups, return only cached groups (for LDAPUF) or return no groups.
        This will return all groups whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON GROUP FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF).
        'attribute' can be 'id' or 'name' for all UF kinds, or anything else for LDAPUF.
        """
        ret = []
        src = self.Groups

        # Use source-specific search methods if available
        if hasattr(src.aq_base, "findGroup"):
            # LDAPUF
            id_attr = src._uid_attr
            if attribute == 'name':
                attr = src._login_attr
            elif attribute == 'id':
                attr = src._uid_attr
            else:
                attr = attribute
            groups = src.findGroup(attr, search_term)
            ret.extend(
                [ u[id_attr] for u in groups ],
                )
        else:
            # Other types of group folder
            search_term = search_term.lower()

            # Find the proper method according to the attribute type
            if attribute == "name":
                method = "getName"
            elif attribute == "id":
                method = "getId"
            else:
                raise NotImplementedError, "Attribute searching is only supported for LDAPGroupFolder by now."

            # Actually search
            for u in self.getGroups():
                s = getattr(u, method)().lower()
                if string.find(s, search_term) != -1:
                    ret.append(u.getId())
        return ret

    security.declareProtected(Permissions.manage_users, "searchGroupsByName")
    def searchGroupsByName(self, search_term):
        """Return group ids whose name match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying group folder:
        it may return all groups, return only cached groups (for LDAPUF) or return no groups.
        This will return all groups whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON GROUP FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF)
        """
        return self.searchGroupsByAttribute("name", search_term)

    security.declareProtected(Permissions.manage_users, "searchGroupsById")
    def searchGroupsById(self, search_term):
        """Return group ids whose id match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying group folder:
        it may return all groups, return only cached groups (for LDAPUF) or return no groups.
        This will return all groups whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON GROUP FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF)
        """
        return self.searchGroupsByAttribute("id", search_term)

    #                                                                           #
    #                         SECURITY MANAGEMENT METHODS                       #
    #                                                                           #

    security.declareProtected(Permissions.manage_users, "setRolesOnUsers")
    def setRolesOnUsers(self, roles, userids):
        """Set a common set of roles for a bunch of user atoms.
        """
        for usr in userids:
            self.userSetRoles(usr, roles)

##    def setUsersOfRole(self, usernames, role):
##        """Sets the users of a role.
##        XXX THIS METHOD SEEMS TO BE SEAMLESS.
##        """
##        raise NotImplementedError, "Not implemented."

    security.declareProtected(Permissions.manage_users, "getUsersOfRole")
    def getUsersOfRole(self, role, object = None):
        """Gets the user (and group) ids having the specified role...
        ...on the specified Zope object if it's not None
        ...on their own information if the object is None.
        NOTA: THIS METHOD IS VERY EXPENSIVE.
        XXX PERFORMANCES HAVE TO BE IMPROVED
        """
        ret = []
        for id in self.getUserIds():
            if role in self.getRolesOfUser(id):
                ret.append(id)
        return tuple(ret)

    security.declarePublic("getRolesOfUser")
    def getRolesOfUser(self, userid):
        """Alias for user.getRoles()
        """
        return self.getUserById(userid).getRoles()

    security.declareProtected(Permissions.manage_users, "userFolderAddRole")
    def userFolderAddRole(self, role):
        """Add a new role. The role will be appended, in fact, in GRUF's surrounding folder.
        """
        if role in self.aq_parent.valid_roles():
            raise ValueError, "Role '%s' already exist" % (role, )
            
        return self.aq_parent._addRole(role)

    security.declareProtected(Permissions.manage_users, "userFolderDelRoles")
    def userFolderDelRoles(self, roles):
        """Delete roles.
        The removed roles will be removed from the UserFolder's users and groups as well,
        so this method can be very time consuming with a large number of users.
        """
        # Check that roles exist
        ud_roles = self.aq_parent.userdefined_roles()
        for r in roles:
            if not r in ud_roles:
                raise ValueError, "Role '%s' is not defined on acl_users' parent folder" % (r, )
        
        # Remove role on all users
        for r in roles:
            for u in self.getUsersOfRole(r, ):
                self.userRemoveRole(u, r, )

        # Actually remove role
        return self.aq_parent._delRoles(roles, None)


    security.declarePublic("userFolderGetRoles")
    def userFolderGetRoles(self, ):
        """
        userFolderGetRoles(self,) => tuple of strings
        List the roles defined at the top of GRUF's folder.
        This includes both user-defined roles and default roles.
        """
        return tuple(self.aq_parent.valid_roles())
        

    # Groups support
    
    security.declareProtected(Permissions.manage_users, "setMembers")
    def setMembers(self, groupid, userids):
        """Set the members of the group
        """
        self.getGroup(groupid).setMembers(userids)

    security.declareProtected(Permissions.manage_users, "addMember")
    def addMember(self, groupid, userid):
        """Add a member to a group
        """
        return self.getGroup(groupid).addMember(userid)

    security.declareProtected(Permissions.manage_users, "removeMember")
    def removeMember(self, groupid, userid):
        """Remove a member from a group.
        """
        return self.getGroup(groupid).removeMember(userid)
        
    security.declareProtected(Permissions.manage_users, "getMemberIds")
    def getMemberIds(self, groupid):
        """Return the list of member ids (groups and users) in this group
        """
        m = self.getGroup(groupid)
        if not m:
            raise ValueError, "Invalid group: '%s'" % groupid
        return self.getGroup(groupid).getMemberIds()

    security.declareProtected(Permissions.manage_users, "getUserMemberIds")
    def getUserMemberIds(self, groupid):
        """Return the list of member ids (groups and users) in this group
        """
        return self.getGroup(groupid).getUserMemberIds()

    security.declareProtected(Permissions.manage_users, "getGroupMemberIds")
    def getGroupMemberIds(self, groupid):
        """Return the list of member ids (groups and users) in this group
        XXX THIS MAY BE VERY EXPENSIVE !
        """
        return self.getGroup(groupid).getGroupMemberIds()

    security.declareProtected(Permissions.manage_users, "hasMember")
    def hasMember(self, groupid, id):
        """Return true if the specified atom id is in the group.
        This is the contrary of IUserAtom.isInGroup(groupid).
        THIS CAN BE VERY EXPENSIVE
        """
        return self.getGroup(groupid).hasMember(id)
    

    # User mutation

##    def setUserId(id, newId):
##        """Change id of a user atom.
##        """

##    def setUserName(id, newName):
##        """Change the name of a user atom.
##        """

    security.declareProtected(Permissions.manage_users, "userSetRoles")
    def userSetRoles(self, id, roles):
        """Change the roles of a user atom.
        """
        self._updateUser(id, roles = roles)

    security.declareProtected(Permissions.manage_users, "userAddRole")
    def userAddRole(self, id, role):
        """Append a role for a user atom
        """
        roles = list(self.getUser(id).getRoles())
        if not role in roles:
            roles.append(role)
            self._updateUser(id, roles = roles)

    security.declareProtected(Permissions.manage_users, "userRemoveRole")
    def userRemoveRole(self, id, role):
        """Remove the role of a user atom. Will NOT complain if role doesn't exist
        """
        roles = list(self.getRolesOfUser(id))
        if role in roles:
            roles.remove(role)
            self._updateUser(id, roles = roles)

    security.declareProtected(Permissions.manage_users, "userSetPassword")
    def userSetPassword(self, id, newPassword):
        """Set the password of a user
        """
        u = self.getPureUser(id)
        if not u:
            raise ValueError, "Invalid pure user id: '%s'" % (id,)
        self._updateUser(u.getId(), password = newPassword, )


    security.declareProtected(Permissions.manage_users, "userGetDomains")
    def userGetDomains(self, id):
        """get domains for a user
        """
        usr = self.getPureUser(id)
        return tuple(usr.getDomains())


    security.declareProtected(Permissions.manage_users, "userSetDomains")
    def userSetDomains(self, id, domains):
        """Set domains for a user
        """
        usr = self.getPureUser(id)
        self._updateUser(usr.getId(), domains = domains, )

    security.declareProtected(Permissions.manage_users, "userAddDomain")
    def userAddDomain(self, id, domain):
        """Append a domain to a user
        """
        usr = self.getPureUser(id)
        domains = list(usr.getDomains())
        if not domain in domains:
            roles.append(domain)
            self._updateUser(usr.getId(), domains = domains, )

    security.declareProtected(Permissions.manage_users, "userRemoveDomain")
    def userRemoveDomain(self, id, domain):
        """Remove a domain from a user
        """
        usr = self.getPureUser(id)
        domains = list(usr.getDomains())
        if not domain in domains:
            raise ValueError, "User '%s' doesn't have domain '%s'" % (id, domain, )
        while domain in domains:
            roles.remove(domain)
        self._updateUser(usr.getId(), domains = domains)
            
    security.declareProtected(Permissions.manage_users, "userSetGroups")
    def userSetGroups(self, id, groupnames):
        """Set the groups of a user
        """
        self._updateUser(id, groups = groupnames)

    security.declareProtected(Permissions.manage_users, "userAddGroup")
    def userAddGroup(self, id, groupname):
        """add a group to a user atom
        """
        groups = list(self.getUserById(id).getGroups())
        if not groupname in groups:
            groups.append(groupname)
            self._updateUser(id, groups = groups)

    security.declareProtected(Permissions.manage_users, "userRemoveGroup")
    def userRemoveGroup(self, id, groupname):
        """remove a group from a user atom.
        """
        groups = list(self.getUserById(id).getGroupNames())
        if groupname.startswith(GROUP_PREFIX):
            groupname = groupname[GROUP_PREFIX_LEN:]
        if groupname in groups:
            groups.remove(groupname)
            self._updateUser(id, groups = groups)


        
    #                                                                           #
    #                             VARIOUS OPERATIONS                            #
    #                                                                           #
    
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


    #                                                                   #
    #                           VARIOUS UTILITIES                       #
    #                                                                   #
    # These methods shouldn't be used directly for most applications,   #
    # but they might be useful for some special processing.             #
    #                                                                   #

    security.declarePublic('getGroupPrefix')
    def getGroupPrefix(self):
        """ group prefix """
        return GROUP_PREFIX

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
        src_id = self.getUser(name).getUserSourceId()
        return self.getUserSource(src_id).getUser(name)

    security.declareProtected(Permissions.manage_users, "getUnwrappedGroup")
    def getUnwrappedGroup(self, name):
        """
        getUnwrappedGroup(self, name) => user object or None

        Same as getUnwrappedUser but for groups.
        """
        return self.Groups.acl_users.getUser(name)

    #                                                                           #
    #                        AUTHENTICATION INTERFACE                           #
    #                                                                           #

    security.declarePrivate("authenticate")
    def authenticate(self, name, password, request):
        """
        Pass the request along to the underlying user-related UserFolder
        object
        THIS METHOD RETURNS A USER OBJECT OR NONE, as specified in the code 
        in AccessControl/User.py.
        We also check for inituser in there.
        """
        # Emergency user checking stuff
        emergency = self._emergency_user
        if name is None:
            return None
        if emergency and name==emergency.getUserName():
            if emergency.authenticate(password, request):
                return emergency
            else:
                return None

        # Usual GRUF authentication
        for src in self.listUserSources():
            # XXX We can imagine putting a try/except here to "ignore"
            # UF errors such as SQL or LDAP shutdown
            u = src.authenticate(name, password, request)
            if u:
                return GRUFUser.GRUFUser(u, self, isGroup = 0, source_id = src.getId()).__of__(self)

        # No acl_users in the Users folder or no user authenticated
        # => we refuse authentication
        return None

    #                                                                           #
    #                               GRUF'S GUTS :-)                             #
    #                                                                           #

    security.declarePrivate("_doAddUser")
    def _doAddUser(self, name, password, roles, domains, groups = (), **kw):
        """
        Create a new user. This should be implemented by subclasses to
        do the actual adding of a user. The 'password' will be the
        original input password, unencrypted. The implementation of this
        method is responsible for performing any needed encryption.
        """
        prefix = GROUP_PREFIX

        # Prepare groups
        roles = list(roles)
        gruf_groups = self.getGroupIds()
        for group in groups:
            if not group.startswith(prefix):
                group = "%s%s" % (prefix, group, )
            if not group in gruf_groups:
                raise ValueError, "Invalid group: '%s'" % (group, )
            roles.append(group)

        # Reset the users overview batch
        self._v_batch_users = []

        # Really add users
        return self.getDefaultUserSource()._doAddUser(
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
        
        # Get actual user name and id
        usr = self.getUser(name)
        id = usr.getRealId()

        # Change groups affectation
        cur_groups = self.getGroups()
        given_roles = tuple(usr.getRoles()) + tuple(roles)
        for group in groups:
            if not group.startswith(GROUP_PREFIX, ):
                group = "%s%s" % (GROUP_PREFIX, group, )
            if not group in cur_groups and not group in given_roles:
                roles.append(group)

        # Reset the users overview batch
        self._v_batch_users = []

        # Change the user itself
        src = usr.getUserSourceId()
        ret = self.getUserSource(src)._doChangeUser(
            id, password, roles, domains, **kw)

        # Invalidate user cache if necessary
        usr.clearCachedGroupsAndRoles()
##        authenticated = getSecurityManager().getUser()
##        if id == authenticated.getId() and hasattr(authenticated, 'clearCachedGroupsAndRoles'):
##            authenticated.clearCachedGroupsAndRoles(self.getUserSource(src).getUser(id))

        return ret

    security.declarePrivate("_updateUser")
    def _updateUser(self, id, password = None, roles = None, domains = None, groups = None):
        """
        _updateUser(self, id, password = None, roles = None, domains = None, groups = None)

        This one should work for users AND groups.
        
        Front-end to _doChangeUser, but with a better default value support.
        We guarantee that None values will let the underlying UF keep the original ones.
        This is not true for the password: some buggy UF implementation may not
        handle None password correctly :-(
        """
        # Get the former values if necessary. Username must be valid !
        usr = self.getUser(id)
        if roles is None:
            # Remove invalid roles and group names
            roles = usr._original_roles
            roles = filter(lambda x: not x.startswith(GROUP_PREFIX), roles)
            roles = filter(lambda x: x not in ('Anonymous', 'Authenticated', 'Shared', ''), roles)
        else:
            # Check if roles are valid
            roles = filter(lambda x: x not in ('Anonymous', 'Authenticated', 'Shared', ''), roles)
            vr = self.userFolderGetRoles()
            for r in roles:
                if not r in vr:
                    raise ValueError, "Invalid or inexistant role: '%s'." % (r, )
        if domains is None:
            domains = usr._original_domains
        if groups is None:
            groups = usr.getGroups(no_recurse = 1)
        else:
            # Check if given groups are valid
            glist = self.getGroupNames()
            glist.extend(map(lambda x: "%s%s" % (GROUP_PREFIX, x), glist))
            for g in groups:
                if not g in glist:
                    raise ValueError, "Invalid group: '%s'" % (g, )

        # Reset the users overview batch
        self._v_batch_users = []

        # Change the user
        return self._doChangeUser(id, password, roles, domains, groups)

    security.declarePrivate("_doDelUsers")
    def _doDelUsers(self, names):
        """
        Delete one or more users. This should be implemented by subclasses
        to do the actual deleting of users.
        This won't delete groups !
        """
        # Collect information about user sources
        sources = {}
        for name in names:
            usr = self.getUser(name, __include_groups__ = 0)
            if not usr:
                continue        # Ignore invalid user names
            src = usr.getUserSourceId()
            if not sources.has_key(src):
                sources[src] = []
            sources[src].append(name)
        for src, names in sources.items():
            self.getUserSource(src)._doDelUsers(names)

        # Reset the users overview batch
        self._v_batch_users = []


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
        prefix = GROUP_PREFIX
        gruf_groups = self.getGroupIds()
        for group in groups:
            if not group.startswith(prefix):
                group = "%s%s" % (prefix, group, )
            if group == "%s%s" % (prefix, name, ):
                raise ValueError, "Infinite recursion for group '%s'." % (group, )
            if not group in gruf_groups:
                raise ValueError, "Invalid group: '%s' (defined groups are %s)" % (group, gruf_groups)
            roles.append(group)

        # Reset the users overview batch
        self._v_batch_users = []

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
            name = name[GROUP_PREFIX_LEN:]

        # Check if group exists
        grp = self.getGroup(name, prefixed = 0)
        if grp is None:
            raise ValueError, "Invalid group: '%s'" % (name,)

        # Change groups affectation
        cur_groups = self.getGroups()
        given_roles = tuple(grp.getRoles()) + tuple(roles)
        for group in groups:
            if not group.startswith(GROUP_PREFIX, ):
                group = "%s%s" % (GROUP_PREFIX, group, )
            if group == "%s%s" % (GROUP_PREFIX, grp.id):
                raise ValueError, "Cannot affect group '%s' to itself!" % (name, )        # Prevent direct inclusion of self
            new_grp = self.getGroup(group)
            if not new_grp:
                raise ValueError, "Invalid or inexistant group: '%s'" % (group, )
            if "%s%s" % (GROUP_PREFIX, grp.id) in new_grp.getGroups():
                raise ValueError, "Cannot affect %s to group '%s' as it would lead to circular references." % (group, name, )        # Prevent indirect inclusion of self
            if not group in cur_groups and not group in given_roles:
                roles.append(group)

        # Reset the users overview batch
        self._v_batch_users = []

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
        _updateGroup(self, name, roles = None, groups = None)

        Front-end to _doChangeUser, but with a better default value support.
        We guarantee that None values will let the underlying UF keep the original ones.
        This is not true for the password: some buggy UF implementation may not
        handle None password correctly but we do not care for Groups.

        group name can be prefixed or not
        """
        # Remove prefix if given
        if name.startswith(self.getGroupPrefix()):
            name = name[GROUP_PREFIX_LEN:]

        # Get the former values if necessary. Username must be valid !
        usr = self.getGroup(name, prefixed = 0)
        if roles is None:
            # Remove invalid roles and group names
            roles = usr._original_roles
            roles = filter(lambda x: not x.startswith(GROUP_PREFIX), roles)
            roles = filter(lambda x: x not in ('Anonymous', 'Authenticated', 'Shared'), roles)
        if groups is None:
            groups = usr.getGroups(no_recurse = 1)

        # Reset the users overview batch
        self._v_batch_users = []

        # Change the user
        return self._doChangeGroup(name, roles, groups)


    security.declarePrivate("_doDelGroup")
    def _doDelGroup(self, name):
        """Delete one user."""
        # Remove prefix if given
        if name.startswith(self.getGroupPrefix()):
            name = name[GROUP_PREFIX_LEN:]

        # Reset the users overview batch
        self._v_batch_users = []

        # Delete it
        return self.Groups.acl_users._doDelUsers([name])

    security.declarePrivate("_doDelGroups")
    def _doDelGroups(self, names):
        """Delete one or more users."""
        for group in names:
            if not self.getGroupByName(group, None):
                continue        # Ignore invalid groups
            self._doDelGroup(group)




    #                                           #
    #      Pretty Management form methods       #
    #                                           #


    security.declarePublic('getGRUFVersion')
    def getGRUFVersion(self,):
        """
        getGRUFVersion(self,) => Return human-readable GRUF version as a string.
        """
        rev_date = "$Date: 2004/07/13 13:07:46 $"[7:-2]
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
            self._updateUser(id = user, groups = groups, roles = roles, )


        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + "/" + obj.getId() + "/manage_workspace")

    security.declareProtected(Permissions.manage_users, "deleteUser")
    def deleteUser(self, user, REQUEST = {}, ):
        """
        deleteUser(self, user, REQUEST = {}, ) => used in ZMI
        """
        pass


    security.declareProtected(Permissions.manage_users, "changeOrCreateUsers")
    def changeOrCreateUsers(self, users = [], groups = [], roles = [], new_users = [], default_password = '', REQUEST = {}, ):
        """
        changeOrCreateUsers => affect roles & groups to users and/or create new users

        All parameters are strings or lists (NOT tuples !).
        NO CHECKING IS DONE. This is an utility method, it's not part of the official API.
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
            if name in map(lambda x: x.getId(), self.getUsers()):
                continue

            # Use default password or generate a random one
            if default_password:
                password = default_password
            else:
                password = ""
                for x in range(0, 8):  # Password will be 8 chars long
                    password = "%s%s" % (password, random.choice("ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"), )
            self._doAddUser(name, password, add_roles, (), add_groups, )

            # Store the newly created password
            passwords_list.append({'name':name, 'password':password})

        # Update existing users
        for user in users:
            self._updateUser(id = user, groups = groups, roles = roles, )

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


    #                                                                   #
    #                   Local Roles Acquisition Blocking                #
    #   Those two methods perform their own security check.             #
    #                                                                   #

    security.declarePublic("acquireLocalRoles")
    def acquireLocalRoles(self, folder, status):
        """
        Enable or disable local role acquisition on the specified folder.
        If status is true, it will enable, else it will disable.
        Note that the user _must_ have the change_permissions permission on the
        folder to allow changes on it.
        If you want to use this code from a product, please use _acquireLocalRoles()
        instead: this private method won't check security on the destination folder.
        It's usually a bad idea to use _acquireLocalRoles() directly in your product,
        but, well, after all, you do what you want ! :^)
        """
        # Perform security check on destination folder
        if not getSecurityManager().checkPermission(Permissions.change_permissions, folder):
            raise Unauthorized(name = "acquireLocalRoles")

        return self._acquireLocalRoles(folder, status)

    security.declarePrivate("acquireLocalRolesUnrestricted")
    def _acquireLocalRoles(self, folder, status):
        """Same as _acquireLocalRoles() but won't perform security check on the folder.
        """
        # Set the variable (or unset it if it's defined)
        if not status:
            folder.__ac_local_roles_block__ = 1
        else:
            if getattr(folder, '__ac_local_roles_block__', None):
                folder.__ac_local_roles_block__ = None


    security.declarePublic("isLocalRoleAcquired")
    def isLocalRoleAcquired(self, folder):
        """Return true if the specified folder allows local role acquisition.
        """
        if getattr(folder, '__ac_local_roles_block__', None):
            return 0
        return 1


    #                                                                                   #
    #                           Security audit and info methods                         #
    #                                                                                   #


    # This method normally has NOT to be public ! It is because of a CMF inconsistancy.
    # folder_localrole_form is accessible to users who have the manage_properties permissions
    # (according to portal_types/Folder/Actions information). This is silly !
    # folder_localrole_form should be, in CMF, accessible only to those who have the
    # manage_users permissions instead of manage_properties permissions.
    # This is yet another one CMF bug we have to care about.
    # To deal with that in Plone2.1, we check for a particular permission on the destination
    # object _inside_ the method.
    security.declarePublic("getLocalRolesForDisplay")
    def getLocalRolesForDisplay(self, object):
        """This is used for plone's local roles display
        This method returns a tuple (massagedUsername, roles, userType, actualUserName).
        This method is protected by the 'access content information' permission. We may
        change that if it's too permissive..."""
        # Perform security check on destination object
        if not getSecurityManager().checkPermission(Permissions.access_contents_information, object):
            raise Unauthorized(name = "getLocalRolesForDisplay")

        return self._getLocalRolesForDisplay(object)

    def _getLocalRolesForDisplay(self, object):
        """This is used for plone's local roles display
        This method returns a tuple (massagedUsername, roles, userType, actualUserName)"""
        result = []
        local_roles = object.get_local_roles()
        prefix = self.getGroupPrefix()
        for one_user in local_roles:
            massagedUsername = username = one_user[0]
            roles = one_user[1]
            userType = 'user'
            if prefix:
                if self.getGroup(username) or \
                   self.getGroup('%s%s' % (prefix, username)):
                    if username.startswith(prefix):
                        massagedUsername = username[len(prefix):]
                    userType = 'group'
            else:
                userType = 'unknown'
            result.append((massagedUsername, roles, userType, username))
        return tuple(result)    


    security.declarePublic("getAllLocalRoles")
    def getAllLocalRoles(self, object):
        """getAllLocalRoles(self, object): return a dictionnary {useratom_id: roles} of local
        roles defined AND herited at a certain point. This will handle lr-blocking
        as well.
        """
        # Perform security check on destination object
        if not getSecurityManager().checkPermission(Permissions.change_permissions, object):
            raise Unauthorized(name = "getAllLocalRoles")
        
        return self._getAllLocalRoles(object)


    def _getAllLocalRoles(self, object):
        """getAllLocalRoles(self, object): return a dictionnary {useratom_id: roles} of local
        roles defined AND herited at a certain point. This will handle lr-blocking
        as well.
        """
        # Modified from AccessControl.User.getRolesInContext().
        merged = {}
        object = getattr(object, 'aq_inner', object)
        while 1:
            if hasattr(object, '__ac_local_roles__'):
                dict = object.__ac_local_roles__ or {}
                if callable(dict): dict = dict()
                for k, v in dict.items():
                    if not merged.has_key(k):
                        merged[k] = {}
                    for role in v:
                        merged[k][role] = 1
            if not self.isLocalRoleAcquired(object):
                break
            if hasattr(object, 'aq_parent'):
                object=object.aq_parent
                object=getattr(object, 'aq_inner', object)
                continue
            if hasattr(object, 'im_self'):
                object=object.im_self
                object=getattr(object, 'aq_inner', object)
                continue
            break
        for key, value in merged.items():
            merged[key] = value.keys()
        return merged
    

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
        XXX HAS TO BE OPTIMIZED
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
        if display_users:
            for u in map(lambda x: x.getId(), self.getPureUsers()):
                obj = self.getUser(u)
                html = obj.asHTML()
                handle = "U%02d" % user_index
                user_index += 1
                ret.append(('user', u, u, handle, html))

        if display_groups:
            for u in self.getGroupNames():
                obj = self.getUser(u)
                handle = "G%02d" % group_index
                html = obj.asHTML()
                group_index += 1
                ret.append(('group', u, obj.getUserNameWithoutGroupPrefix(), handle, html))

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
            icon = string.join(self.getPhysicalPath(), '/') + '/img_group'
##            icon = self.absolute_url() + '/img_group'
        else:
            icon = ' img_user'
##            icon = self.absolute_url() + '/img_user'

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
        # Use the cache at first
        if self._v_no_tree and self._v_cache_no_tree > time.time():
            return []        # Do not use the tree

        # XXX - I DISABLE THE TREE BY NOW (Pb. with icon URL)
        return []

        # Then, use a simple computation to determine opportunity to use the tree or not
        ngroups = len(self.getGroupNames())
        if ngroups > MAX_TREE_USERS_AND_GROUPS:
            self._v_no_tree = 1
            self._v_cache_no_tree = time.time() + TREE_CACHE_TIME
            return []
        nusers = len(self.getUsers())
        if ngroups + nusers > MAX_TREE_USERS_AND_GROUPS:
            meth_list = self.getGroups
        else:
            meth_list = self.getUsers
        self._v_no_tree = 0

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

        # Use individual usr/grp management screen (only if name is passed along the mgt URL)
        if username != "acl_users":
            if username in map(lambda x: x.getId(), self.getUsers()):
                REQUEST.set('username', username)
                REQUEST.set('MANAGE_TABS_NO_BANNER', '1')   # Prevent use of the manage banner
                return self.restrictedTraverse('manage_user')()

        # Default management screen
        return self.restrictedTraverse('manage_overview')()


    # Tree caching information
    _v_no_tree =  0
    _v_cache_no_tree = 0
    _v_cache_tree = (0, [])


    def __bobo_traverse__(self, request, name):
        """
        Looks for the name of a user or a group.
        This applies only if users list is not huge.
        """
        # Check if it's an attribute
        if hasattr(self.aq_base, name, ):
            return getattr(self, name)

        # It's not an attribute, maybe it's a user/group
        # (this feature is used for the tree)
        if name.startswith('_'):
            pass        # Do not fetch users
        elif name.startswith('manage_'):
            pass        # Do not fetch users
        elif name in INVALID_USER_NAMES:
            pass        # Do not fetch users
        else:
            # Only try to get users is fetch_user is true.
            # This is only for performance reasons.
            # The following code block represent what we want to minimize
            if self._v_cache_tree[0] < time.time():
                un = map(lambda x: x.getId(), self.getUsers())            # This is the cost we want to avoid
                self._v_cache_tree = (time.time() + TREE_CACHE_TIME, un, )
            else:
                un = self._v_cache_tree[1]

            # Get the user if we can
            if name in un:
                self._v_no_tree = 0
                return self

            # Force getting the user if we must
            if request.get("FORCE_USER"):
                self._v_no_tree = 0
                return self

        # This will raise if it's not possible to acquire 'name'
        return getattr(self, name, )




    #                                                                                   #
    #                           USERS / GROUPS BATCHING (ZMI SCREENS)                   #
    #                                                                                   #

    _v_batch_users = []

    security.declareProtected(Permissions.view_management_screens, "listUsersBatches")
    def listUsersBatches(self,):
        """
        listUsersBatches(self,) => return a list of (start, end) tuples.
        Return None if batching is not necessary
        """
        # Time-consuming stuff !
        un = map(lambda x: x.getId(), self.getPureUsers())
        if len(un) <= MAX_USERS_PER_PAGE:
            return None
        un.sort()

        # Split this list into small groups if necessary
        ret = []
        idx = 0
        l_un = len(un)
        nbatches = int(math.ceil(l_un / float(MAX_USERS_PER_PAGE)))
        for idx in range(0, nbatches):
            first = idx * MAX_USERS_PER_PAGE
            last = first + MAX_USERS_PER_PAGE - 1
            if last >= l_un:
                last = l_un - 1
            # Append a tuple (not dict) to avoid too much memory consumption
            ret.append((first, last, un[first], un[last]))

        # Cache & return it
        self._v_batch_users = un
        return ret

    security.declareProtected(Permissions.view_management_screens, "getUsersBatchTable")
    def listUsersBatchTable(self,):
        """
        listUsersBatchTable(self,) => Same a mgt screens but divided into sublists to
        present them into 5 columns.
        XXX have to merge this w/getUsersBatch to make it in one single pass
        """
        # Iterate
        ret = []
        idx = 0
        current = []
        for rec in (self.listUsersBatches() or []):
            if not idx % 5:
                if current:
                    ret.append(current)
                current = []
            current.append(rec)
            idx += 1

        if current:
            ret.append(current)

        return ret

    security.declareProtected(Permissions.view_management_screens, "getUsersBatch")
    def getUsersBatch(self, start):
        """
        getUsersBatch(self, start) => user list
        """
        # Rebuild the list if necessary
        if not self._v_batch_users:
            un = map(lambda x: x.getId(), self.getPureUsers())
            self._v_batch_users = un

        # Return the batch
        end = start + MAX_USERS_PER_PAGE
        ids = self._v_batch_users[start:end]
        ret = []
        for id in ids:
            usr = self.getUser(id)
            if usr:                     # Prevent adding invalid users
                ret.append(usr)
        return ret


    #                                                                            #
    #                         Multiple sources management                        #
    #                                                                            #

    # Arrows
    img_up_arrow = ImageFile.ImageFile('www/up_arrow.gif', globals())
    img_down_arrow = ImageFile.ImageFile('www/down_arrow.gif', globals())
    img_up_arrow_grey = ImageFile.ImageFile('www/up_arrow_grey.gif', globals())
    img_down_arrow_grey = ImageFile.ImageFile('www/down_arrow_grey.gif', globals())

    security.declareProtected(Permissions.manage_users, "listUserSources")
    def listUserSources(self, ):
        """
        listUserSources(self, ) => Return a list of userfolder objects
        Only return VALID (ie containing an acl_users) user sources if all is None
        XXX HAS TO BE OPTIMIZED VERY MUCH!
        """
        ret = []
        for src in self.objectValues(['GRUFUsers']):
            if 'acl_users' in src.objectIds():
                ret.append(src.acl_users)                       # XXX possible security hole ?
                                                                # we cannot use restrictedTraverse here because
                                                                # of infinite recursion issues.
        ret.sort(lambda x,y: cmp(x.aq_parent.id, y.aq_parent.id))    # XXX speed improvements to do there
        return ret

    security.declareProtected(Permissions.manage_users, "listUserSourceFolders")
    def listUserSourceFolders(self, ):
        """
        listUserSources(self, ) => Return a list of GRUFUsers objects
        """
        ret = []
        for src in self.objectValues(['GRUFUsers']):
            ret.append(src)
        ret.sort(lambda x,y: cmp(x.id, y.id))
        return ret

    security.declarePrivate("getUserSource")
    def getUserSource(self, id):
        """
        getUserSource(self, id) => GRUFUsers.acl_users object.
        Raises if no acl_users available
        """
        return getattr(self, id).acl_users

    security.declarePrivate("getUserSourceFolder")
    def getUserSourceFolder(self, id):
        """
        getUserSourceFolder(self, id) => GRUFUsers object
        """
        return getattr(self, id)

    security.declareProtected(Permissions.manage_users, "addUserSource")
    def addUserSource(self, factory_uri, REQUEST = {}, *args, **kw):
        """
        addUserSource(self, factory_uri, REQUEST = {}, *args, **kw) => redirect
        Adds the specified user folder
        """
        # Get the initial Users id
        ids = self.objectIds('GRUFUsers')
        if ids:
            ids.sort()
            if ids == ['Users',]:
                last = 0
            else:
                last = int(ids[-1][-2:])
            next_id = "Users%02d" % (last + 1, )
        else:
            next_id = "Users"

        # Add the GRUFFolder object
        uf = GRUFFolder.GRUFUsers(id = next_id)
        self._setObject(next_id, uf)

##        # If we use ldap, tag it
##        if string.find(factory_uri.lower(), "ldap") > -1:
##            self._haveLDAPUF += 1

        # Add its underlying UserFolder
        # If we're called TTW, uses a redirect else tries to call the UF factory directly
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect("%s/%s/%s" % (self.absolute_url(), next_id, factory_uri))
        return getattr(self, next_id).unrestrictedTraverse(factory_uri)(*args, **kw)

    security.declareProtected(Permissions.manage_users, "deleteUserSource")
    def deleteUserSource(self, id = None, REQUEST = {}):
        """
        deleteUserSource(self, id = None, REQUEST = {}) => Delete the specified user source
        """
        # Check the source id
        if type(id) != type('s'):
            raise ValueError, "You must choose a valid source to delete and confirm it."

        # Delete it
        self.manage_delObjects([id,])
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_GRUFSources')


    security.declareProtected(Permissions.manage_users, "getDefaultUserSource")
    def getDefaultUserSource(self,):
        """
        getDefaultUserSource(self,) => acl_users object
        Return default user source for user writing.
        XXX By now, the FIRST source is the default one. This may change in the future.
        """
        lst = self.listUserSources()
        if not lst:
            raise RuntimeError, "No valid User Source to add users in."
        return lst[0]


    security.declareProtected(Permissions.manage_users, "listAvailableUserSources")
    def listAvailableUserSources(self, filter_permissions = 1, filter_classes = 1):
        """
        listAvailableUserSources(self, filter_permissions = 1, filter_classes = 1) => tuples (name, factory_uri)
        List UserFolder replacement candidates.

        - if filter_classes is true, return only ones which have a base UserFolder class
        - if filter_permissions, return only types the user has rights to add
        """
        ret = []

        # Fetch candidate types
        user = getSecurityManager().getUser()
        meta_types = []
        if callable(self.all_meta_types):
            all=self.all_meta_types()
        else:
            all=self.all_meta_types
        for meta_type in all:
            if filter_permissions and meta_type.has_key('permission'):
                if user.has_permission(meta_type['permission'],self):
                    meta_types.append(meta_type)
            else:
                meta_types.append(meta_type)

        # Keep only, if needed, BasicUserFolder-derived classes
        for t in meta_types:
            if t['name'] == self.meta_type:
                continue        # Do not keep GRUF ! ;-)

            if filter_classes:
                try:
                    if t.get('instance', None) and t['instance'].isAUserFolder:
                        ret.append((t['name'], t['action']))
                        continue
                    if t.get('instance', None) and class_utility.isBaseClass(AccessControl.User.BasicUserFolder, t['instance']):
                        ret.append((t['name'], t['action']))
                        continue
                except AttributeError:
                    pass        # We ignore 'invalid' instances (ie. that wouldn't define a __base__ attribute)
            else:
                ret.append((t['name'], t['action']))

        return tuple(ret)

    security.declareProtected(Permissions.manage_users, "moveUserSourceUp")
    def moveUserSourceUp(self, id, REQUEST = {}):
        """
        moveUserSourceUp(self, id, REQUEST = {}) => used in management screens
        try to get ids as consistant as possible
        """
        # List and sort sources and preliminary checks
        ids = self.objectIds('GRUFUsers')
        ids.sort()
        if not ids or not id in ids:
            raise ValueError, "Invalid User Source: '%s'" % (id,)

        # Find indexes to swap
        src_index = ids.index(id)
        if src_index == 0:
            raise ValueError, "Cannot move '%s'  User Source up." % (id, )
        dest_index = src_index - 1

        # Find numbers to swap, fix them if they have more than 1 as offset
        if ids[dest_index] == 'Users':
            dest_num = 0
        else:
            dest_num = int(ids[dest_index][-2:])
        src_num = dest_num + 1

        # Get ids
        src_id = id
        if dest_num == 0:
            dest_id = "Users"
        else:
            dest_id = "Users%02d" % (dest_num,)
        tmp_id = "%s_" % (dest_id, )

        # Perform the swap
        self._renameUserSource(src_id, tmp_id)
        self._renameUserSource(dest_id, src_id)
        self._renameUserSource(tmp_id, dest_id)

        # Return back to the forms
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_GRUFSources')


    security.declareProtected(Permissions.manage_users, "moveUserSourceDown")
    def moveUserSourceDown(self, id, REQUEST = {}):
        """
        moveUserSourceDown(self, id, REQUEST = {}) => used in management screens
        try to get ids as consistant as possible
        """
        # List and sort sources and preliminary checks
        ids = self.objectIds('GRUFUsers')
        ids.sort()
        if not ids or not id in ids:
            raise ValueError, "Invalid User Source: '%s'" % (id,)

        # Find indexes to swap
        src_index = ids.index(id)
        if src_index == len(ids) - 1:
            raise ValueError, "Cannot move '%s'  User Source up." % (id, )
        dest_index = src_index + 1

        # Find numbers to swap, fix them if they have more than 1 as offset
        if id == 'Users':
            dest_num = 1
        else:
            dest_num = int(ids[dest_index][-2:])
        src_num = dest_num - 1

        # Get ids
        src_id = id
        if dest_num == 0:
            dest_id = "Users"
        else:
            dest_id = "Users%02d" % (dest_num,)
        tmp_id = "%s_" % (dest_id, )

        # Perform the swap
        self._renameUserSource(src_id, tmp_id)
        self._renameUserSource(dest_id, src_id)
        self._renameUserSource(tmp_id, dest_id)

        # Return back to the forms
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_GRUFSources')



    security.declarePrivate('_renameUserSource')
    def _renameUserSource(self, id, new_id, ):
        """
        Rename a particular sub-object.
        Taken fro CopySupport.manage_renameObject() code, modified to disable verifications.
        """
        try: self._checkId(new_id)
        except: raise CopyError, MessageDialog(
                      title='Invalid Id',
                      message=sys.exc_info()[1],
                      action ='manage_main')
        ob=self._getOb(id)
##        if not ob.cb_isMoveable():
##            raise "Copy Error", eNotSupported % id
##        self._verifyObjectPaste(ob)           # This is what we disable
        try:    ob._notifyOfCopyTo(self, op=1)
        except: raise CopyError, MessageDialog(
                      title='Rename Error',
                      message=sys.exc_info()[1],
                      action ='manage_main')
        self._delObject(id)
        ob = aq_base(ob)
        ob._setId(new_id)

        # Note - because a rename always keeps the same context, we
        # can just leave the ownership info unchanged.
        self._setObject(new_id, ob, set_owner=0)


    security.declareProtected(Permissions.manage_users, "replaceUserSources")
    def replaceUserSource(self, id = None, new_factory = None, REQUEST = {}, *args, **kw):
        """
        replaceUserSource(self, id = None, new_factory = None, REQUEST = {}, *args, **kw) => perform user source replacement

        If new_factory is None, find it inside REQUEST (useful for ZMI screens)
        """
        # Check the source id
        if type(id) != type('s'):
            raise ValueError, "You must choose a valid source to replace and confirm it."

        # Retreive factory if not explicitly passed
        if not new_factory:
            for record in REQUEST.get("source_rec", []):
                if record['id'] == id:
                    new_factory = record['new_factory']
                    break
            if not new_factory:
                raise ValueError, "You must select a new User Folder type."

        # Delete the former one
        us = getattr(self, id)
        if "acl_users" in us.objectIds():
            us.manage_delObjects(['acl_users'])

##        # If we use ldap, tag it
##        if string.find(new_factory.lower(), "ldap") > -1:
##            self._haveLDAPUF += 1

        # Re-create the underlying UserFolder
        # If we're called TTW, uses a redirect else tries to call the UF factory directly
        if REQUEST.has_key('RESPONSE'):
            return REQUEST.RESPONSE.redirect("%s/%s/%s" % (self.absolute_url(), id, new_factory))
        return us.unrestrictedTraverse(new_factory)(*args, **kw) # XXX minor security pb ?


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
