import time, traceback

# Zope imports
from Globals import DTMLFile, InitializeClass
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from AccessControl.User import SimpleUser
from AccessControl.Permissions import view_management_screens, manage_users
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime

import GroupUserFolder

from global_symbols import *

# LDAPUserFolder package imports
from Products.LDAPUserFolder.SimpleCache import SimpleCache

addLDAPGroupFolderForm = DTMLFile('dtml/addLDAPGroupFolder', globals())


class LDAPGroupFolder(SimpleItem):
    """ """
    security = ClassSecurityInfo()

    meta_type = 'LDAPGroupFolder'
    id = 'acl_users'

    isPrincipiaFolderish=1
    isAUserFolder=1

    manage_options=(
        ({'label' : 'Groups', 'action' : 'manage_main',},)
        + SimpleItem.manage_options
        )

    security.declareProtected(view_management_screens, 'manage_main')
    manage_main = DTMLFile('dtml/groups', globals())
    
    
    def __setstate__(self, v):
        """ """
        LDAPGroupFolder.inheritedAttribute('__setstate__')(self, v)

        self._cache = SimpleCache()
        self._cache.setTimeout(600)
        self._cache.clear()

    def __init__( self, title, luf=''):
        """ """
        self._luf = luf
        self._cache = SimpleCache()
        self._cache.setTimeout(600)
        self._cache.clear()

    security.declarePrivate(manage_users, 'getGRUF')
    def getGRUF(self):
        """ """
        return self.aq_parent.aq_parent


    security.declareProtected(manage_users, 'getLUF')
    def getLUF(self):
        """ """
        s = self.getGRUF().getUserSource(self._luf)
        if getattr(s, 'meta_type', None) != "LDAPUserFolder":
            # whoops, we moved LDAPUF... let's try to find it back
            Log(LOG_WARNING, "LDAPUserFolder moved. Trying to find it back.")
            s = None
            for src in self.getGRUF().listUserSources():
                if src.meta_type == "LDAPUserFolder":
                    self._luf = src.getPhysicalPath()[-2]
                    s = src
                    break
            if not s:
                raise RuntimeError, "You must change your groups source in GRUF if you do not have a LDAPUserFolder as a users source."
        return s


    security.declareProtected(manage_users, 'getGroups')
    def getGroups(self, dn='*', attr=None, pwd=''):
        """ """
        return self.getLUF().getGroups(dn, attr, pwd)


    security.declareProtected(manage_users, 'getGroupType')
    def getGroupType(self, group_dn):
        """ """
        return self.getLUF().getGroupType(group_dn)

    security.declareProtected(manage_users, 'getGroupMappings')
    def getGroupMappings(self):
        """ """
        return self.getLUF().getGroupMappings()

    security.declareProtected(manage_users, 'manage_addGroupMapping')
    def manage_addGroupMapping(self, group_name, role_name, REQUEST=None):
        """ """
        self._cache.remove(group_name)
        self.getLUF().manage_addGroupMapping(group_name, role_name, None)

        if REQUEST:
            msg = 'Added LDAP group to Zope role mapping: %s -> %s' % (
                group_name, role_name)
            return self.manage_main(manage_tabs_message=msg)

    security.declareProtected(manage_users, 'manage_deleteGroupMappings')
    def manage_deleteGroupMappings(self, group_names, REQUEST=None):
        """ Delete mappings from LDAP group to Zope role """
        self._cache.clear()
        self.getLUF().manage_deleteGroupMappings(group_names, None)
        if REQUEST:
            msg = 'Deleted LDAP group to Zope role mapping for: %s' % (
                ', '.join(group_names))
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_addGroup')
    def manage_addGroup( self
                       , newgroup_name
                       , newgroup_type='groupOfUniqueNames'
                       , REQUEST=None
                       ):
        """Add a new group in groups_base.
        """
        self.getLUF().manage_addGroup(newgroup_name, newgroup_type, None)
        
        if REQUEST:
            msg = 'Added new group %s' % (newgroup_name)
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_deleteGroups')
    def manage_deleteGroups(self, dns=[], REQUEST=None):
        """ Delete groups from groups_base """
        self.getLUF().manage_deleteGroups(dns, None)
        self._cache.clear()
 
        if REQUEST:
            msg = 'Deleted group(s):<br> %s' % '<br>'.join(dns)
            return self.manage_main(manage_tabs_message=msg)

    security.declareProtected(manage_users, 'getUser')
    def getUser(self, name):
        """ """
        # Get the group from the cache
        user = self._cache.get(name, '')
        if user:
            return user

        # Scan groups to find the proper user.
        # THIS MAY BE EXPENSIVE AND HAS TO BE OPTIMIZED...
        grps = self.getLUF().getGroups()
        valid_roles = self.userFolderGetRoles()
        dn = None
        for n, g_dn in grps:
            if n == name:
                dn = g_dn
                break
        if not dn:
            return None

        # Current mapping
        roles = self.getLUF()._mapRoles([name])

        # Nested groups
        groups = list(self.getLUF().getGroups(dn=dn, attr='cn', ))
        roles.extend(self.getLUF()._mapRoles(groups))

        # !!! start test
        Log(LOG_DEBUG, name, "roles", groups, roles)
        Log(LOG_DEBUG, name, "mapping", getattr(self.getLUF(), '_groups_mappings', {}))
        # !!! end test

        actual_roles = []
        for r in roles:
            if r in valid_roles:
                actual_roles.append(r)
            elif "%s%s" % (GROUP_PREFIX, r) in valid_roles:
                actual_roles.append("%s%s" % (GROUP_PREFIX, r))
        Log(LOG_DEBUG, name, "actual roles", actual_roles)
        user = GroupUser(n, '', actual_roles, [])
        self._cache.set(name, user)
        return user
        
    security.declareProtected(manage_users, 'getUserNames')
    def getUserNames(self):
        """ """
        return [g[0] for g in self.getLUF().getGroups()]

    security.declareProtected(manage_users, 'getUsers')
    def getUsers(self, authenticated=1):
        """ """
        data = []
        
        grps = self.getLUF().getGroups()
        valid_roles = self.userFolderGetRoles()
        for n, dn in grps:
            # Group mapping
            roles = self.getLUF()._mapRoles([n])
            
            # nested groups
            groups = list(self.getLUF().getGroups(dn=dn, attr='cn', ))
            roles.extend(self.getLUF()._mapRoles(groups))

            # computation
            actual_roles = []
            for r in roles:
                if r in valid_roles:
                    actual_roles.append(r)
                elif "%s%s" % (GROUP_PREFIX, r) in valid_roles:
                    actual_roles.append("%s%s" % (GROUP_PREFIX, r))
            user = GroupUser(n, '', actual_roles, [])
            data.append(user)

        return data

    security.declarePrivate('_doAddUser')
    def _doAddUser(self, name, password, roles, domains, **kw):
        """WARNING: If a role with exists with the same name as the group, we do not add
        the group mapping for it, but we create it as if it were a Zope ROLE.
        Ie. it's not possible to have a GRUF Group name = a Zope role name, BUT,
        with this system, it's possible to differenciate between LDAP groups and LDAP roles.
        """
        self.getLUF().manage_addGroup(name)
        self._doChangeUser(name, password, roles, domains, **kw)

    security.declarePrivate('_doDelUsers')
    def _doDelUsers(self, names):
        dns = []
        luf = self.getLUF()
        for g_name, dn in luf.getGroups():
            if g_name in names:
                dns.append(dn)
        self._cache.clear()
        return luf.manage_deleteGroups(dns)

    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, domains, **kw):
        """WARNING: If a role with exists with the same name as the group, we do not add
        the group mapping for it, but we create it as if it were a Zope ROLE.
        Ie. it's not possible to have a GRUF Group name = a Zope role name, BUT,
        with this system, it's possible to differenciate between LDAP groups and LDAP roles.
        """
        luf = self.getLUF()
        self._cache.remove(name)

        # Get group DN
        dn = None
        for g_name, g_dn in luf.getGroups():
            if g_name == name:
                dn = g_dn
                break
        if not dn:
            raise ValueError, "Invalid LDAP group: '%s'" % (name, )
                
        # Edit group mappings
##        if name in self.aq_parent.valid_roles():
##            # This is, in fact, a role
##            self.getLUF().manage_addGroupMapping(name, name)
##        else:
##            # This is a group -> we set it as a group
##            self.getLUF().manage_addGroupMapping(name, self.getGroupPrefix() + name)

        # Change roles
        if luf._local_groups:
            luf.manage_editUserRoles(dn, roles)
        else:
            # We have to transform roles into group dns: transform them as a dict
            role_dns = []
            all_groups = luf.getGroups()
            all_roles = luf.valid_roles()
            groups = {}
            for g in all_groups:
                groups[g[0]] = g[1]

            # LDAPUF does the mistake of adding possibly invalid roles to the user roles
            # (for example, adding the cn of a group additionnaly to the mapped zope role).
            # So we must remove from our 'roles' list all roles which are prefixed by group prefix
            # but are not actually groups.
            # If a group has the same name as a role, we assume that it should be a _role_.
            # We should check against group/role mapping here, but... well... XXX TODO !
            # See "HERE IT IS" comment below.

            # Scan roles we are asking for to manage groups correctly
            for role in roles:
                if not role in all_roles:
                    continue                        # Do not allow propagation of invalid roles
                if role.startswith(GROUP_PREFIX):
                    role = role[GROUP_PREFIX_LEN:]            # Remove group prefix : groups are stored WITHOUT prefix in LDAP
                    if role in all_roles:
                        continue                            # HERE IT IS
                r = groups.get(role, None)
                if not r:
                    Log(LOG_WARNING, "LDAP Server doesn't provide a '%s' group (asked for user '%s')." % (role, name, ))
                    continue
                role_dns.append(r)

            # Perform the change
            luf.manage_editGroupRoles(dn, role_dns)



def manage_addLDAPGroupFolder( self, title = '', luf='', REQUEST=None):
    """ """
    this_folder = self.this()

    if hasattr(aq_base(this_folder), 'acl_users') and REQUEST is not None:
        msg = 'This+object+already+contains+a+User+Folder'

    else:
        # Try to guess where is LUF
        if not luf:
            for src in this_folder.listUserSources():
                if src.meta_type == "LDAPUserFolder":
                    luf = src.aq_parent.getId()

        # No LUF found : error
        if not luf:
            raise KeyError, "You must be within GRUF with a LDAPUserFolder as one of your user sources."
            
        n = LDAPGroupFolder( title, luf )

        this_folder._setObject('acl_users', n)
        this_folder.__allow_groups__ = self.acl_users
        
        msg = 'Added+LDAPGroupFolder'
 
    # return to the parent object's manage_main
    if REQUEST:
        url = REQUEST['URL1']
        qs = 'manage_tabs_message=%s' % msg
        REQUEST.RESPONSE.redirect('%s/manage_main?%s' % (url, qs))


InitializeClass(LDAPGroupFolder)


class GroupUser(SimpleUser):
    """ """

    def __init__(self, name, password, roles, domains):
        SimpleUser.__init__(self, name, password, roles, domains)
        self._created = time.time()

    def getCreationTime(self):
        """ """
        return DateTime(self._created)
