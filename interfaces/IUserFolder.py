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
        Return a list of all possible user atom ids (not names) in the system.
        WARNING: This method should be called, in fact, 'getUserIds' but
        we want to ensure backward compatibility. Please see the id Vs. name
        consideration at the top of this document. So, groups will be returned
        with their prefix by this method
        [NOTA: This method is time-expensive !]
        """
        
    def getUser(id):
        """Return the named user atom object or None
        """

    def getUsers():
        """Return a list of user atom objects.
        In case of some UF implementations, the returned object may only be a subset
        of all possible users.
        In other words, you CANNOT assert that len(getUsers()) equals len(getUserNames()).
        With cache-support UserFolders, such as LDAPUserFolder, the getUser() method will
        return only cached user objects instead of fetching all possible users.
        """

    def getUserById(id):
        """Return the user atom corresponding to the given id. This is an alias for getUser(id)
        """

    def getUserByName(name):
        """Same as getUser() but works with a name instead of an id.
        [NOTA: Theorically, the id is a handle, while the name is the actual login name.
        But difference between a user id and a user name is unsignificant in
        all current User Folder implementations... except for GROUPS.]        
        """

    # User access

    def getPureUserNames():
        """Same as getUserNames() but without groups
        """

    def getPureUsers():
        """Same as getUsers() but without groups.
        """
        
    # Group access

    def getGroupNames():
        """Same as getUserNames() but without pure users.
        """

    def getGroups():
        """Same as getUsers() but without pure users.
        """

    def getGroupById(id):
        """Same as getUserById(id) but forces returning a group.
        """

    def getGroupByName(name):
        """Same as getUserByName(name) but forces returning a group.
        """
    

    # Mutators

    def userFolderAddUser(id, password, roles, domains, groups, **kw):
        """API method for creating a new user object. Note that not all
        user folder implementations support dynamic creation of user
        objects.
        """
    def userFolderEditUser(id, password, roles, domains, groups, **kw):
        """API method for changing user object attributes. Note that not
        all user folder implementations support changing of user object
        attributes."""

    def userFolderDelUsers(ids):
        """API method for deleting one or more user atom objects. Note that not
        all user folder implementations support deletion of user objects."""

    def userFolderAddGroup(id, roles, groups, **kw):
        """API method for creating a new group.
        """
        
    def userFolderEditGroup(id, roles, groups, **kw):
        """API method for changing group object attributes.
        """

    def userFolderDelGroups(ids):
        """API method for deleting one or more group objects.
        Implem. note : All ids must be prefixed with 'group_',
        so this method ends up beeing only a filter of non-prefixed ids
        before calling userFolderDelUsers().
        """

    def setId(id, newId):
        """Change id of a user atom.
        """

    def setName(id, newName):
        """Change the name of a user atom.
        """

    def setRoles(id, roles):
        """Change the roles of a user atom
        """

    def addRole(id, role):
        """Append a role for a user atom
        """

    def removeRole(id, role):
        """Remove the role of a user atom
        """

    def setPassword(id, newPassword):
        """Set the password of a user
        """

    def setDomains(id, domains):
        """Set domains for a user
        """

    def addDomain(id, domain):
        """Append a domain to a user
        """

    def removeDomain(id, domain):
        """Remove a domain from a user
        """

    def setGroups(userid, groupids):
        """Set the groups of a user
        """

    def addGroup(id, group):
        """add a group to a user atom
        """

    def removeGroup(id, group):
        """remove a group from a user atom
        """


    # Security management

    def setRolesOnUsers(roles, userids):
        """Set a common set of roles for a bunch of user atoms.
        """

    def setUsersOfRole(usernames, role):
        """Sets the users of a role.
        XXX THIS METHOD SEEMS TO BE SEAMLESS.
        """

    def getUsersOfRole(role, object = None):
        """Gets the users having the specified role...
        ...on the specified Zope object if it's not None
        ...on their own information if the object is None.
        NOTA: THIS METHOD IS VERY EXPENSIVE.
        """

    def userFolderAddRole(role):
        """Add a new role. The role will be appended, in fact, in GRUF's surrounding folder.
        """

    def userFolderDelRoles(roles):
        """Delete roles.
        The removed roles will be removed from the UserFolder's users and groups as well,
        so this method can be very time consuming with a large number of users.
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
        

class IUserAtom(Interface):
    """
    This interface is an abstract representation of what both a User and a Group can do.
    """
    # Accessors
    
    def getId():
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's
        UserDatabase"""

    def getName():
        """Get user's or group's name.
        For a user, the name can be set by the underlying user folder but usually id == name.
        For a group, the ID is prefixed, but the NAME is NOT prefixed by 'group_'.
        """

    def getRoles():
        """Return the list of roles assigned to a user atom.
        This will never return gruf-related roles.
        """


    # Mutators

    def setId(newId):
        """Set the id of the user or group. This might change its name as well.
        """

    def setName(newName):
        """Set the name of the user or group. Depending on the UserFolder implementation,
        this might change the id as well.
        """

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

    def getGroups():
        """Return the names of the groups that the user or group is a member of.
        Return an empty list if the user or group doesn't belong to any group."""

    def getAllGroups():
        """
        Return the all the groups names (including transitive ones)  
        that the user or group is a member of
        """

    def isInGroup(groupid):
        """Return 1 if the user is member of the specified group id
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


class IUser(IUserAtom):
    """
    A user is a user atom who can log itself on, and
    have additional properties such as domains and password.
    """
    
    # Accessors
    
    def getUserName():
        """Return the username of a user; alias for getName()"""

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
    def getMembers(self):
        """Return the member ids (users and groups) of the atoms of this group"""

    def getUserMembers(self):
        """Return the member ids (users only) of the users of this group"""

    def getGroupMembers(self):
        """Return the members ids (groups only) of the groups of this group"""

    def hasMember(id):
        """Return true if the specified atom id is in the group.
        This is the contrary of IUserAtom.isInGroup(groupid)"""

    def addUser(userid):
        """Add a user the the current group"""
        
    def removeUser(userid):
        """Remove a user from the current group"""

