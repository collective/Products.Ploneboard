# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# initially written by J Cameron Cooper, 11 June 2003
# concept with Brent Hendricks, George Runyan

""" Group data tool interface

Goes along the lines of portal_memberdata, but for groups.
"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_groupdata(Interface):
    """ A helper tool for portal_groups that transparently adds
    properties to groups and provides convenience methods"""

##    id = Attribute('id', "Must be set to 'portal_groupdata'")

    def wrapGroup(g):
        """ Returns an object implementing the GroupData interface"""


class GroupData(Interface):
    """ An abstract interface for accessing properties on a group object"""

    def setProperties(properties=None, **kw):
        """Allows setting of group properties en masse.
        Properties can be given either as a dict or a keyword parameters list"""

    def getProperty(id):
        """ Return the value of the property specified by 'id' """

    def getProperties():
        """ Return the properties of this group. Properties are as usual in Zope."""

    def getGroupId():
        """ Return the string id of this group, WITHOUT group prefix."""

    def getMemberId():
        """This exists only for a basic user/group API compatibility
        """

    def getGroupName():
        """ Return the name of the group."""

    def getGroupMembers():
        """ Return a list of the portal_memberdata-ish members of the group."""

    def getGroupMemberIds():
        """ Return a list of the user ids of the group."""

    def addMember(id):
        """ Add the existing member with the given id to the group"""

    def removeMember(id):
        """ Remove the member with the provided id from the group """

    def getGroup():
        """ Returns the actual group implementation. Varies by group
        implementation (GRUF/Nux/et al)."""
