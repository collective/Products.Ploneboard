from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


"""
VOCABULARY:

  - [Pure] User: A user is a user atom who can log itself on, and
    have additional properties such as domains and password.

  - Group: A group is a user atom other atoms can belong to.

  - User atom: Abstract representation of either a User or
    a Group.

  - Member (of a group): User atom inside a group.

  - Name (of an atom): For a user, the name can be set by
    the underlying user folder but usually id == name.
    For a group, its id is prefixed, but its name is NOT prefixed by 'group_'.
    For method taking a name instead of an id (eg. getUserByName()),
    if a user and a group have the same name,
    the USER will have precedence over the group.
"""

class IUserFolder(Interface):

    #                                                   #
    #           Regular Zope UserFolder API             #
    #                                                   #

    # User atom access
    
    def getUserNames():
        """
        Return a list of all possible user atom names in the system.
        Groups will be returned WITHOUT their prefix by this method.
        So, there might be a collision between a user name and a group name.
        [NOTA: This method is time-expensive !]
        """

    def getUserIds():
        """
        Return a list of all possible user atom ids in the system.
        WARNING: Please see the id Vs. name consideration at the
        top of this document. So, groups will be returned
        WITH their prefix by this method
        [NOTA: This method is time-expensive !]
        """
        
    def getUser(name):
        """Return the named user atom object or None
        NOTA: If no user can be found, we try to append a group prefix
        and fetch the user again before returning 'None'. This will ensure
        backward compatibility. So in fact, both group id and group name can be
        specified to this method.
        """

    def getUsers():
        """Return a list of user atom objects in the users cache.
        In case of some UF implementations, the returned object may only be a subset
        of all possible users.
        In other words, you CANNOT assert that len(getUsers()) equals len(getUserNames()).
        With cache-support UserFolders, such as LDAPUserFolder, the getUser() method will
        return only cached user objects instead of fetching all possible users.
        So this method won't be very time-expensive, but won't be accurate !
        """

    def getUserById(id, default):
        """Return the user atom corresponding to the given id.
        If default is provided, return default if no user found, else raise an exception
        """

    def getUserByName(name, default):
        """Same as getUserById() but works with a name instead of an id.
        If default is provided, return default if no user found, else raise an exception
        [NOTA: Theorically, the id is a handle, while the name is the actual login name.
        But difference between a user id and a user name is unsignificant in
        all current User Folder implementations... except for GROUPS.]        
        """

    # Search interface for users; they won't return groups in any case.

    def searchUsersByName(search_term):
        """Return user ids which match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        """

    def searchUsersById(search_term):
        """Return users whose id match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        """
        
    def searchUsersByAttribute(attribute, search_term):
        """Return user ids whose 'attribute' match the specified search_term.
        If search_term is an empty string, behaviour depends on the underlying user folder:
        it may return all users, return only cached users (for LDAPUF) or return no users.
        This will return all users whose name contains search_term (whaterver its case).
        THIS METHOD MAY BE VERY EXPENSIVE ON USER FOLDER KINDS WHICH DO NOT PROVIDE A
        SEARCHING METHOD (ie. every UF kind except LDAPUF).
        'attribute' can be 'id' or 'name' for all UF kinds, or anything else for LDAPUF.
        """


    # User access

    def getPureUserNames():
        """Same as getUserNames() but without groups
        """

    def getPureUserIds():
        """Same as getUserIds() but without groups
        """

    def getPureUsers():
        """Same as getUsers() but without groups.
        """

    def getPureUser(id):
        """Same as getUser() but forces returning a user and not a group
        """
        
    # Group access

    def getGroupNames():
        """Same as getUserNames() but without pure users.
        """

    def getGroupIds():
        """Same as getUserIds() but without pure users.
        """

    def getGroups():
        """Same as getUsers() but without pure users.
        In case of some UF implementations, the returned object may only be a subset
        of all possible users.
        In other words, you CANNOT assert that len(getUsers()) equals len(getUserNames()).
        With cache-support UserFolders, such as LDAPUserFolder, the getUser() method will
        return only cached user objects instead of fetching all possible users.
        So this method won't be very time-expensive, but won't be accurate !
        """

    def getGroup(name):
        """Return the named group object or None. As usual, 'id' is prefixed.
        """

    def getGroupById(id):
        """Same as getUserById(id) but forces returning a group.
        """

    def getGroupByName(name):
        """Same as getUserByName(name) but forces returning a group.
        The specified name MUST NOT be prefixed !
        """
    

    # Mutators

    def userFolderAddUser(name, password, roles, domains, groups, **kw):
        """API method for creating a new user object. Note that not all
        user folder implementations support dynamic creation of user
        objects.
        Groups can be specified by name or by id (preferabily by name)."""

    def userFolderEditUser(name, password, roles, domains, groups, **kw):
        """API method for changing user object attributes. Note that not
        all user folder implementations support changing of user object
        attributes.
        Groups can be specified by name or by id (preferabily by name)."""

    def userFolderDelUsers(names):
        """API method for deleting one or more user atom objects. Note that not
        all user folder implementations support deletion of user objects."""

    def userFolderAddGroup(name, roles, groups, **kw):
        """API method for creating a new group.
        """
        
    def userFolderEditGroup(name, roles, groups, **kw):
        """API method for changing group object attributes.
        """

    def userFolderDelGroups(names):
        """API method for deleting one or more group objects.
        Implem. note : All ids must be prefixed with 'group_',
        so this method ends up beeing only a filter of non-prefixed ids
        before calling userFolderDelUsers().
        """

    # User mutation

    
    # XXX do we have to allow a user to be renamed ?
##    def setUserId(id, newId):
##        """Change id of a user atom. The user name might be changed as well by this operation.
##        """

##    def setUserName(id, newName):
##        """Change the name of a user atom. The user id might be changed as well by this operation.
##        """

    def userSetRoles(id, roles):
        """Change the roles of a user atom
        """

    def userAddRole(id, role):
        """Append a role for a user atom
        """

    def userRemoveRole(id, role):
        """Remove the role of a user atom.
        This will not, of course, affect implicitly-acquired roles from the user groups.
        """

    def userSetPassword(id, newPassword):
        """Set the password of a user
        """

    def userSetDomains(id, domains):
        """Set domains for a user
        """

    def userGetDomains(id, ):
        """Get domains for a user
        """

    def userAddDomain(id, domain):
        """Append a domain to a user
        """

    def userRemoveDomain(id, domain):
        """Remove a domain from a user
        """

    def userSetGroups(userid, groupnames):
        """Set the groups of a user. Groupnames are, as usual, not prefixed.
        However, a groupid can be given as a fallback
        """

    def userAddGroup(id, groupname):
        """add a group to a user atom. Groupnames are, as usual, not prefixed.
        However, a groupid can be given as a fallback
        """

    def userRemoveGroup(id, groupname):
        """remove a group from a user atom. Groupnames are, as usual, not prefixed.
        However, a groupid can be given as a fallback
        """


    # Security management

    def setRolesOnUsers(roles, userids):
        """Set a common set of roles for a bunch of user atoms.
        """

##    def setUsersOfRole(usernames, role):
##        """Sets the users of a role.
##        XXX THIS METHOD SEEMS TO BE SEAMLESS.
##        """

    def getUsersOfRole(role, object = None):
        """Gets the user (and group) ids having the specified role...
        ...on the specified Zope object if it's not None
        ...on their own information if the object is None.
        NOTA: THIS METHOD IS VERY EXPENSIVE.
        """

    def getRolesOfUser(userid):
        """Alias for user.getRoles()
        """

    def userFolderAddRole(role):
        """Add a new role. The role will be appended, in fact, in GRUF's surrounding folder.
        """

    def userFolderDelRoles(roles):
        """Delete roles.
        The removed roles will be removed from the UserFolder's users and groups as well,
        so this method can be very time consuming with a large number of users.
        """

    def userFolderGetRoles():
        """List the roles defined at the top of GRUF's folder.
        """


    # Groups support
    def setMembers(groupid, userids):
        """Set the members of the group
        """

    def addMember(groupid, id):
        """Add a member to a group
        """

    def removeMember(groupid, id):
        """Remove a member from a group
        """

    def hasMember(groupid, id):
        """Return true if the specified atom id is in the group.
        This is the contrary of IUserAtom.isInGroup(groupid).
        THIS CAN BE VERY EXPENSIVE"""

    def getMemberIds(groupid):
        """Return the list of member ids (groups and users) in this group.
        It will unmangle nested groups as well.
        THIS METHOD CAN BE VERY EXPENSIVE AS IT NEEDS TO FETCH ALL USERS.
        """

    def getUserMemberIds(groupid):
        """Same as listMemberIds but only return user ids
        THIS METHOD CAN BE VERY EXPENSIVE AS IT NEEDS TO FETCH ALL USERS.
        """

    def getGroupMemberIds(groupid):
        """Same as listMemberUserIds but only return group ids.
        THIS METHOD CAN BE VERY EXPENSIVE AS IT NEEDS TO FETCH ALL USERS.
        """
        

class IUserAtom(Interface):
    """
    This interface is an abstract representation of what both a User and a Group can do.
    """
    # Accessors
    
    def getId(unprefixed = 0):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's UserDatabase.
        If unprefixed, remove all prefixes in any case."""

    def getUserName():
        """Alias for getName()
        """

    def getName():
        """Get user's or group's name.
        For a user, the name can be set by the underlying user folder but usually id == name.
        For a group, the ID is prefixed, but the NAME is NOT prefixed by 'group_'.
        """

    def getRoles():
        """Return the list of roles assigned to a user atom.
        This will never return gruf-related roles.
        """

    # Properties are defined depending on the underlying user folder: some support
    # properties mutation (such as LDAPUserFolder), some do not (such as regular UF).

    def getProperty(name):
        """Get a property's value.
        Will raise if not available.
        """

    def hasProperty(name):
        """Return true if the underlying user object has a value for the property.
        """

    # Mutators

    def setProperty(name, value):
        """Set a property's value.
        As some user folders cannot set properties, this method is not guaranteed to work
        and will raise a NotImplementedError if the underlying user folder cannot store
        properties (or _this_ particular property) for a user.
        """
        
    # XXX We do not allow user name / id changes
##    def setId(newId):
##        """Set the id of the user or group. This might change its name as well.
##        """

##    def setName(newName):
##        """Set the name of the user or group. Depending on the UserFolder implementation,
##        this might change the id as well.
##        """

    def setRoles(roles):
        """Change user's roles
        """

    def addRole(role):
        """Append a role to the user
        """

    def removeRole(role):
        """Remove a role from the user's ones
        """

    # Security-related methods

    def getRolesInContext(object):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""

    def has_permission(permission, object):
        """Check to see if a user has a given permission on an object."""

    def allowed(object, object_roles=None):
        """Check whether the user has access to object. The user must
           have one of the roles in object_roles to allow access."""

    def has_role(roles, object=None):
        """Check to see if a user has a given role or roles."""



    # Group management

    # XXX TODO: CLARIFY ID VS. NAME

    def isGroup():
        """Return true if this atom is a group.
        """

    def getGroupNames():
        """Return the names of the groups that the user or group is directly a member of.
        Return an empty list if the user or group doesn't belong to any group.
        Doesn't include transitive groups."""

    def getGroupIds():
        """Return the names of the groups that the user or group is a member of.
        Return an empty list if the user or group doesn't belong to any group.
        Doesn't include transitive groups."""

    def getGroups():
        """getAllGroupIds() alias.
        Return the IDS (not names) of the groups that the user or group is a member of.
        Return an empty list if the user or group doesn't belong to any group.
        THIS WILL INCLUDE TRANSITIVE GROUPS AS WELL."""

    def getAllGroupIds():
        """Return the names of the groups that the user or group is a member of.
        Return an empty list if the user or group doesn't belong to any group.
        Include transitive groups."""

    def getAllGroupNames():
        """Return the names of the groups that the user or group is directly a member of.
        Return an empty list if the user or group doesn't belong to any group.
        Include transitive groups."""

    def isInGroup(groupid):
        """Return true if the user is member of the specified group id
        (including transitive groups)"""

    def setGroups(groupids):
        """Set 'groupids' groups for the user or group.
        """

    def addGroup(groupid):
        """Append a group to the current object's groups.
        """

    def removeGroup(groupid):
        """Remove a group from the object's groups
        """

    def getRealId():
        """Return group id WITHOUT group prefix.
        For a user, return regular user id.
        This method is essentially internal.
        """


class IUser(IUserAtom):
    """
    A user is a user atom who can log itself on, and
    have additional properties such as domains and password.
    """
    
    # Accessors

    def getDomains():
        """Return the list of domain restrictions for a user"""

    # Mutators
    
    def setPassword(newPassword):
        """Set user's password
        """

    def setDomains(domains):
        """Replace domains for the user
        """

    def addDomain(domain):
        """Append a domain for the user
        """

    def removeDomain(domain):
        """Remove a domain for the user
        """


class IGroup(Interface):
    """
    A group is a user atom other atoms can belong to.
    """
    def getMemberIds():
        """Return the member ids (users and groups) of the atoms of this group.
        This method can be very expensive !"""

    def getUserMemberIds():
        """Return the member ids (users only) of the users of this group"""

    def getGroupMemberIds():
        """Return the members ids (groups only) of the groups of this group"""

    def hasMember(id):
        """Return true if the specified atom id is in the group.
        This is the contrary of IUserAtom.isInGroup(groupid)"""

    def addMember(userid):
         """Add a user the the current group"""
         
    def removeMember(userid):
         """Remove a user from the current group"""
