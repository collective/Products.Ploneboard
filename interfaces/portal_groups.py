# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# initially written by J Cameron Cooper, 11 June 2003
# concept with Brent Hendricks, George Runyan

""" Groups tool interface

Goes along the lines of portal_membership, but for groups."""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_groups(Interface):
    """Defines an interface for working with groups in an abstract manner.
    Parallels the portal_membership interface of CMFCore"""
    id = Attribute('id','Must be set to "portal_groups')

    def getGroupById(id):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""

    def listGroups():
        """Returns a list of the available portal_groupdata-ish objects."""

    def listGroupIds():
        """Returns a list of the available groups' ids."""

    def searchForGroups(REQUEST, **kw):    # maybe searchGroups()?
        """Return a list of groups meeting certain conditions. """
        # arguments need to be better refined?

    def addGroup(self, id, password, roles, domains):
        """Create a group with the supplied id, roles, and domains.

	Underlying user folder must support adding users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""

    def editGroup(self, id, password, roles, permissions):
        """Edit the given group with the supplied password, roles, and domains.

	Underlying user folder must support editing users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""

    def removeGroups(self, ids):
        """Remove the group in the provided list (if possible).

	Underlying user folder must support removing users via the usual Zope API."""

    def createGrouparea(id):
        """Create a space in the portal for the given group, much like member home
        folders."""

    def getGroupareaFolder(id):
        """Returns the object of the group's work area."""

    def getGroupareaURL(id):
        """Returns the full URL to the group's work area."""

    # and various roles things...

