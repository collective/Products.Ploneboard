##############################################################################
#
# Copyright (c) 2003 The Connexions Project and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic group data tool.

$Id: GroupDataTool.py,v 1.9 2003/12/17 15:35:14 pjgrizel Exp $
"""

from Products.CMFCore.utils import UniqueObject, getToolByName
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import DTMLFile
from Globals import InitializeClass
from AccessControl.Role import RoleManager
from BTrees.OOBTree import OOBTree
from ZPublisher.Converters import type_converters
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import SetOwnProperties
from Products.CMFCore.ActionProviderBase import ActionProviderBase

# Try/except around this to avoid import errors on Plone 1.0.3
# XXX jcc => can you check this, please ?
try:
    from Products.CMFCore.MemberDataTool import CleanupTemp
    _have_cleanup_temp = 1
except:
    _have_cleanup_temp = None

from interfaces.portal_groupdata import portal_groupdata as IGroupDataTool
from interfaces.portal_groupdata import GroupData as IGroupData

_marker = []  # Create a new marker object.


class GroupDataTool (UniqueObject, SimpleItem, PropertyManager, ActionProviderBase):
    """ This tool wraps group objects, allowing transparent access to properties.
    """
    # The latter will work only with Plone 1.1 => hence, the if
    if hasattr(ActionProviderBase, '__implements__'):
        __implements__ = (IGroupDataTool, ActionProviderBase.__implements__)

    id = 'portal_groupdata'
    meta_type = 'CMF Group Data Tool'
    _actions = ()

    _v_temps = None
    _properties=({'id':'title', 'type': 'string', 'mode': 'wd'},)

    security = ClassSecurityInfo()

    manage_options=( ActionProviderBase.manage_options +
                     ({ 'label' : 'Overview'
                       , 'action' : 'manage_overview'
                       },
#                     , { 'label' : 'Contents'
#                       , 'action' : 'manage_showContents'
#                       }
                     )
                   + PropertyManager.manage_options
                   + SimpleItem.manage_options
                   )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainGroupDataTool', globals())

    #security.declareProtected(ViewManagementScreens, 'manage_showContents')
    #manage_showContents = DTMLFile('dtml/groupdataContents', globals())


    def __init__(self):
        self._members = OOBTree()
        # Create the default properties.
        self._setProperty('description', '', 'text')
        self._setProperty('email', '', 'string')
        self._setProperty('listed', '', 'boolean')

    #
    #   'portal_groupdata' interface methods
    #
    security.declarePrivate('wrapGroup')
    def wrapGroup(self, g):
        """Returns an object implementing the GroupData interface"""
        id = g.getId()
        members = self._members
        if not members.has_key(id):
            # Get a temporary member that might be
            # registered later via registerMemberData().
            temps = self._v_temps
            if temps is not None and temps.has_key(id):
                portal_group = temps[id]
            else:
                base = aq_base(self)
                portal_group = GroupData(base, id)
                if temps is None:
                    self._v_temps = {id:portal_group}
                    if hasattr(self, 'REQUEST'):
                        # No REQUEST during tests.
                        # XXX jcc => CleanupTemp doesn't seem to work on Plone 1.0.3.
                        # Have to find a way to pass around...
                        if _have_cleanup_temp:
                            self.REQUEST._hold(CleanupTemp(self))
                else:
                    temps[id] = portal_group
        else:
            portal_group = members[id]
        # Return a wrapper with self as containment and
        # the user as context.
        return portal_group.__of__(self).__of__(g)

    security.declarePrivate('registerGroupData')
    def registerGroupData(self, g, id):
        '''
        Adds the given member data to the _members dict.
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        '''
        self._members[id] = g


InitializeClass(GroupDataTool)


class GroupData (SimpleItem):

    __implements__ = IGroupData

    security = ClassSecurityInfo()

    def __init__(self, tool, id):
        self.id = id
        # Make a temporary reference to the tool.
        # The reference will be removed by notifyModified().
        self._tool = tool

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        # Links self to parent for full persistence.
        tool = getattr(self, '_tool', None)
        if tool is not None:
            del self._tool
            tool.registerGroupData(self, self.getId())

    security.declarePublic('getGroup')
    def getGroup(self):
        """ Returns the actual group implementation. Varies by group
        implementation (GRUF/Nux/et al). In GRUF this is a user object."""
        # The user object is our context, but it's possible for
        # restricted code to strip context while retaining
        # containment.  Therefore we need a simple security check.
        parent = aq_parent(self)
        bcontext = aq_base(parent)
        bcontainer = aq_base(aq_parent(aq_inner(self)))
        if bcontext is bcontainer or not hasattr(bcontext, 'getUserName'):
            raise 'GroupDataError', "Can't find group data"
        # Return the user object, which is our context.
        return parent

    def getTool(self):
        return aq_parent(aq_inner(self))

    security.declarePublic('getGroupMembers')
    def getGroupMembers(self):
        """
        Returns a list of the portal_memberdata-ish members of the group.
        """
        md = self.portal_memberdata
        gd = self.portal_groupdata
        ret = []
        for usr in self.getGroup().getGroupUsers():
            if usr.isGroup():
                ret.append(gd.wrapGroup(usr))
            else:
                ret.append(md.wrapUser(usr))
        return ret

    # FIXME: What permission should this be?
    security.declarePublic('addMember')
    def addMember(self, id):
        """ Add the existing member with the given id to the group"""
	user = self.acl_users.getUser(id)
        prefix = self.acl_users.getGroupPrefix()

        groups = list(user.getGroups())
        groups.append(prefix + self.getGroupName())
        self.acl_users.getDefaultUserSource().userFolderEditUser(id, None, user.getRoles()+tuple(groups), user.getDomains())


    # FIXME: What permission should this be?
    security.declarePublic('removeMember')
    def removeMember(self, id):
        """ Remove the member with the provided id from the group """
        user = self.acl_users.getUser(id)
        prefix = self.acl_users.getGroupPrefix()

        groups = list(user.getGroups())
        groups.remove(prefix + self.getGroupName())
        self.acl_users.getDefaultUserSource().userFolderEditUser(id, None, user.getRoles()+tuple(groups), user.getDomains())

    security.declareProtected(SetOwnProperties, 'setProperties')
    def setProperties(self, properties=None, **kw):
        '''Allows the authenticated member to set his/her own properties.
        Accepts either keyword arguments or a mapping for the "properties"
        argument.
        '''
        if properties is None:
            properties = kw
        membership = getToolByName(self, 'portal_groups')
        registration = getToolByName(self, 'portal_registration', None)
        if not membership.isAnonymousUser():
            member = membership.getAuthenticatedMember()
            if registration:
                failMessage = registration.testPropertiesValidity(properties, member)
                if failMessage is not None:
                    raise 'Bad Request', failMessage
            member.setMemberProperties(properties)
        else:
            raise 'Bad Request', 'Not logged in.'

    security.declarePublic('setGroupProperties')
    def setGroupProperties(self, mapping):
        '''Sets the properties of the member.
        '''
        # Sets the properties given in the MemberDataTool.
        tool = self.getTool()
        for id in tool.propertyIds():
            if mapping.has_key(id):
                if not self.__class__.__dict__.has_key(id):
                    value = mapping[id]
                    if type(value)==type(''):
                        proptype = tool.getPropertyType(id) or 'string'
                        if type_converters.has_key(proptype):
                            value = type_converters[proptype](value)
                    setattr(self, id, value)
        # Hopefully we can later make notifyModified() implicit.
        self.notifyModified()

    # XXX: s.b., getPropertyForMember(member, id, default)?

    security.declarePublic('getProperty')
    def getProperty(self, id, default=_marker):
        """ Returns the value of the property specified by 'id' """
        tool = self.getTool()
        base = aq_base( self )

        # First, check the wrapper (w/o acquisition).
        value = getattr( base, id, _marker )
        if value is not _marker:
            return value

        # Then, check the tool and the user object for a value.
        tool_value = tool.getProperty( id, _marker )
        user_value = getattr( self.getGroup(), id, _marker )

        # If the tool doesn't have the property, use user_value or default
        if tool_value is _marker:
            if user_value is not _marker:
                return user_value
            elif default is not _marker:
                return default
            else:
                raise ValueError, 'The property %s does not exist' % id

        # If the tool has an empty property and we have a user_value, use it
        if not tool_value and user_value is not _marker:
            return user_value

        # Otherwise return the tool value
        return tool_value

    def __str__(self):
        return self.getGroupId()



    security.declarePublic("isGroup")
    def isGroup(self,):
        """
        isGroup(self,) => Return true if this is a group.
        Will always return true for groups
        """
        return 1
    

    ### Group object interface ###

    security.declarePublic('getGroupName')
    def getGroupName(self):
        """Return the name of the group, without any special decorations (like GRUF prefixes.)"""
        return self.getGroup().getUserNameWithoutGroupPrefix()

    security.declarePublic('getId')
    def getGroupId(self):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's UserDatabase"""
        return self.getGroup().getId()

    security.declarePublic('getRoles')
    def getRoles(self):
	"""Return the list of roles assigned to a user."""
	return self.getGroup().getRoles()

    security.declarePublic('getRolesInContext')
    def getRolesInContext(self, object):
        """Return the list of roles assigned to the user,  including local
	roles assigned in context of the passed in object."""
	return self.getGroup().getRolesInContext(object)

    security.declarePublic('getDomains')
    def getDomains(self):
	"""Return the list of domain restrictions for a user"""
	return self.getGroup().getDomains()

    security.declarePublic('has_role')
    def has_role(self, roles, object=None):
	"""Check to see if a user has a given role or roles."""
	return self.getGroup().has_role(roles, object)

    # There are other parts of the interface but they are
    # deprecated for use with CMF applications.

InitializeClass(GroupData)
