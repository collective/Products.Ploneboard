# Re-define a few methods

from global_symbols import *


# These mandatory attributes are required by LDAP schema.
# They will be filled with user name as a default value.
# You have to provide a gruf_ldap_required_fields python script
# in your Plone's skins if you want to override this.
MANDATORY_ATTRIBUTES = ("sn", "cn", )


def _doAddUser(self, name, password, roles, domains, **kw):
    """
    Special user adding method for use with LDAPUserFolder.
    This will ensure parameters are correct for LDAP management
    """
    kwargs = {}               # We will pass this dict
    attrs = {}

    # Get gruf_ldap_required_fields result and fill in mandatory stuff
    if hasattr(self, "gruf_ldap_required_fields"):
        attrs = self.gruf_ldap_required_fields(login = name)
    else:
        for attr in MANDATORY_ATTRIBUTES:
            attrs[attr] = name
    kwargs.update(attrs)

    # We assume that name is rdn attribute
    rdn_attr = self._rdnattr
    kwargs[rdn_attr] = name

    # Manage password(s)
    kwargs['user_pw'] = password
    kwargs['confirm_pw'] = password

    # Mangle roles
    kwargs['user_roles'] = self._mangleRoles(name, roles)

    # Delegate to LDAPUF default method
    msg = self.manage_addUser(kwargs = kwargs)
    if msg:
        raise RuntimeError, msg


def _doDelUsers(self, names):
    """
    Remove a bunch of users from LDAP.
    We have to call manage_deleteUsers but, before, we need to find their dn.
    """
    dns = []
    for name in names:
        dns.append(self._find_user_dn(name))

    self.manage_deleteUsers(dns)


def _find_user_dn(self, name):
    """
    Convert a name to an LDAP dn
    """
    # Search records matching name
    rdn_attr = self._rdnattr
    v = self.findUser(search_param = rdn_attr, search_term = name)

    # Filter to keep exact matches only
    v = filter(lambda x: x[rdn_attr] == name, v)

    # Now, decide what to do
    l = len(v)
    if not l:
        # Invalid name
        raise "Invalid user name: '%s'" % (name, )
    elif l > 1:
        # Several records... don't know how to handle
        raise "Duplicate user name for '%s'" % (name, )
    return v[0]['dn']


def _mangleRoles(self, name, roles):
    """
    Return role_dns for this user
    """
    # Local groups => the easiest part
    if self._local_groups:
        return roles

    # We have to transform roles into group dns: transform them as a dict
    role_dns = []
    all_groups = self.getGroups()
    all_roles = self.valid_roles()
    groups = {}
    for g in all_groups:
        groups[g[0]] = g[1]

    # LDAPUF does the mistake of adding possibly invalid roles to the user roles
    # (for example, adding the cn of a group additionnaly to the mapped zope role).
    # So we must remove from our 'roles' list all roles which are prefixed by group prefix
    # but are not actually groups.
    # See http://www.dataflake.org/tracker/issue_00376 for more information on that
    # particular issue.
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
            Log(LOG_WARNING, "LDAP Server doesn't provide a '%s' group (required for user '%s')." % (role, name, ))
        role_dns.append(r)

    return role_dns


def _doChangeUser(self, name, password, roles, domains, **kw):
    """
    Update a user
    """
    # Find the dn at first
    dn = self._find_user_dn(name)
    
    # Change password
    if password is not None:
        if password == '':
            raise ValueError, "Password must not be empty for LDAP users."
        self.manage_editUserPassword(dn, password)
        
    # Perform role change
    self.manage_editUserRoles(dn, self._mangleRoles(name, roles))

    # (No domain management with LDAP.)

    
def manage_editGroupRoles(self, user_dn, role_dns=[], REQUEST=None):
    """ Edit the roles (groups) of a group """
    from Products.LDAPUserFolder.utils import ldap_scopes, GROUP_MEMBER_MAP, filter_format
    from Products.LDAPUserFolder.LDAPDelegate import ADD, DELETE, REPLACE, BASE

    msg = ""

##    Log(LOG_DEBUG, "assigning", role_dns, "to", user_dn)
    all_groups = self.getGroups(attr='dn')
    cur_groups = self.getGroups(dn=user_dn, attr='dn')
    group_dns = []
    for group in role_dns:
        if group.find('=') == -1:
            group_dns.append('cn=%s,%s' % (group, self.groups_base))
        else:
            group_dns.append(group)

    if self._local_groups:
        if len(role_dns) == 0:
            del self._groups_store[user_dn]
        else:
            self._groups_store[user_dn] = role_dns

    else:
        for group in all_groups:
            member_attr = GROUP_MEMBER_MAP.get(self.getGroupType(group))

            if group in cur_groups and group not in group_dns:
                action = DELETE
            elif group in group_dns and group not in cur_groups:
                action = ADD
            else:
                action = None
            if action is not None:
                msg = self._delegate.modify(
                    group
                    , action
                    , {member_attr : [user_dn]}
                    )
##                Log(LOG_DEBUG, "group", group, "subgroup", user_dn, "result", msg)

    if msg:
        raise RuntimeError, msg
