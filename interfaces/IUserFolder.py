from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface



class IUserFolder(Interface):

    #                                                   #
    #           Regular Zope UserFolder API             #
    #                                                   #

    # User access
    
    def getUserNames():
        """
        Return a list of all possible usernames in the system.
        [NOTA: This method is time-expensive !]
        """
    def getUser(name):
        """Return the named user object or None"""

    def getUsers():
        """Return a list of user objects.
        In case of some UF implementations, the returned object may only be a subset
        of all possible users.
        In other words, you cannot assert that len(getUsers()) equals len(getUserNames()).
        With cache-support UserFolders, such as LDAPUserFolder, the getUser() method will
        return only cached user objects instead of fetching all possible users.
        """
    def getUserById(id):
        """
        Return the user corresponding to the given id.
        Same as getUser but works with an id instead of a name.
        [NOTA: Theorically, the id is a handle, while the name is the actual login name.
        But difference between a user id and a user name is unsignificant in
        all current User Folder implementations. ]
        """

    # Mutators

    def userFolderAddUser(name, password, roles, domains, groups, **kw):
        """
        API method for creating a new user object. Note that not all
        user folder implementations support dynamic creation of user
        objects.
        """
    def userFolderEditUser(name, password, roles, domains, groups, **kw):
        """API method for changing user object attributes. Note that not
           all user folder implementations support changing of user object
           attributes."""

    def userFolderDelUsers(names):
        """API method for deleting one or more user objects. Note that not
           all user folder implementations support deletion of user objects."""

    # Security management

    def setRolesOfUser(roles, name):
        """Sets the users of a role"""

    def setUsersOfRole(names, role):
        """Sets the users of a role"""

    def getUsersOfRole(role):
        """Gets the users of a role"""

    def userFolderAddRole(role):
        """Add a new role."""

    def userFolderDelRoles(rolenames):
        """Delete roles."""

    #                                                                   #
    #                           Groups support                          #
    #                                                                   #


    def getGroupNames():
        """Return a list of group names
        """

    def getGroupById(id):
        """Return a group
        """

    def setGroupsOfUser(groupnames, username):
        """Set the groups of a user
        """

    def setUsersOfGroup(usernames, groupname):
        """Set the users of the group
        """

    def userFolderAddGroup(name, roles, groups, **kw):
        """Create a group
        """

    def userFolderEditGroup(name, roles, groups, **kw):
        """Edit a group"""

    def userFolderDelGroups(groupnames):
        """Delete groups
        """


class IUser(Interface):
    def getUserName():
        """Return the username of a user"""

    def getId():
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's
        UserDatabase"""

    def getDomains():
        """Return the list of domain restrictions for a user"""

    def getRoles():
        """Return the list of roles assigned to a user."""

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
    def getParentGroups():
        """Return the names of the groups that the user is a member of"""

    def getAllParentGroups():
         """
         Return the all the groups names (including transitive ones)  
         that the user is a member of
         """

    def isMemberOfGroup(groupname):
        """Return 1 if the user belongs to the specified groupname
        (including transitive groups)"""


class IGroup(Interface):
    def getUsers(self):
        """Returns the members of the group"""

    def getGroups(self):
        """Return the names of the groups of this group"""

    def getAllParentGroups():
         """
         Return the all the groups names (including transitive ones)  
         that the user is a member of
         """

    def getParentGroups():
        """Return the names of the groups that the group is a member of"""

    def attachUser(user):
         """Attach a user the the current group"""
         
    def removeUser(self, user):
         """Remove a user from the current group"""
