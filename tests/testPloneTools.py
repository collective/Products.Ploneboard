#                                                       #
#                 Test GroupUserFolder                  #
#                                                       #
#                                                       #
# (c)2002 Ingeniweb                                     #


import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Permissions / security
from AccessControl.Permissions import access_contents_information, view, add_documents_images_and_files, change_images_and_files, view_management_screens
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl import Unauthorized
from AccessControl.User import UnrestrictedUser

import urllib
import string

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

    
# Get global vars
#from Products.GroupUserFolder.global_symbols import *
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.GroupUserFolder.interfaces import IUserFolder
from Products.GroupUserFolder import GroupUserFolder
from Products.GroupUserFolder import GroupsTool
from Products.GroupUserFolder import GroupDataTool
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')

import GRUFTestCase 
import testInterface
from Log import *



class GroupTestCase(PloneTestCase.PloneTestCase, ):
    
    def afterSetUp(self):
        # Basic assignements
        self.membership = self.portal.portal_membership
        self.gruf = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.prefix = self.gruf.getGroupPrefix()
        self.groups.groupWorkspacesCreationFlag = 0

        # Intial data
        self.groups.addGroup("grp")
        self.groups.addGroup("g1")
        self.groups.addGroup("g2")
        self.groups.addGroup("g3")
        self.groups.addGroup("g4")
        self.membership.addMember("u1", "secret", [], [])
        self.membership.addMember("u2", "secret", [], [])
        self.membership.addMember("u3", "secret", [], [])
        self.membership.addMember("u4", "secret", [], [])
        self.membership.addMember("u5", "secret", [], [])
        self.membership.addMember("u6", "secret", [], [])
        self.membership.addMember("u7", "secret", [], [])
        self.gruf.addMember("g1", "u2")
        self.gruf.addMember("g1", "u3")
        self.gruf.addMember("g1", "u4")
        self.gruf.addMember("g2", "u3")
        self.gruf.addMember("g2", "u4")
        self.gruf.addMember("g2", "u5")
        self.gruf.addMember("g3", "u4")
        self.gruf.addMember("g3", "u5")
        self.gruf.addMember("g3", "u6")
        self.gruf.addMember("g4", "u7")




class TestGroupsTool(GroupTestCase, testInterface.TestInterface):
    klasses = (        # tell which classes to check
        GroupsTool.GroupsTool,
        )
    ignore_interfaces = (
        ActionProviderBase.__implements__,
    )

    def test_getGroupById(self, ):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""
        # Create a dummy group
        self.portal.portal_groups.addGroup("mygroup",)

        # Get group
        g = self.portal.portal_groups.getGroupById("mygroup")
        self.failUnless(g, "Emtpy or invalid group")

    def test_getGroupsByUserId(self, ):
        """Returns a list of the groups the user corresponding to 'userid' belongs to."""
        grps = self.groups.getGroupsByUserId("u3")
        ids = map(lambda x: x.getGroupName(), grps)
        ids.sort()
        self.failUnless(ids == ["g1", "g2", ], "Invalid groups: '%s'" % (ids, ))

    def test_listGroups(self, ):
        """Returns a list of the available portal_groupdata-ish objects."""
        grps = self.groups.listGroups()
        ids = map(lambda x: x.getGroupName(), grps)
        self.failUnless(ids == ["g1", "g2", "g3", "g4", "grp", ], "Invalid groups list: '%s'" % (ids, ))

    def test_listGroupIds(self, ):
        """Returns a list of the available groups' ids."""
        ids = self.groups.listGroupIds()
        ids.sort()
        self.failUnless(ids == ["g1", "g2", "g3", "g4", "grp", ], "Invalid groups list: '%s'" % (ids, ))

    def test_listGroupNames(self, ):
        """Returns a list of the available groups' ids."""
        ids = self.groups.listGroupNames()
        ids.sort()
        self.failUnless(ids == ["g1", "g2", "g3", "g4", "grp", ], "Invalid groups list: '%s'" % (ids, ))

    def test_searchForGroups(self, ):    # maybe searchGroups()?
        """Return a list of groups meeting certain conditions. """
        # arguments need to be better refined?

    def test_addGroup(self, ):
        """Create a group with the supplied id, roles, and domains.

        Underlying user folder must support adding users via the usual Zope API.
        Passwords for groups seem to be currently irrelevant in GRUF."""

    def test_editGroup(self, ):
        """Edit the given group with the supplied password, roles, and domains.

        Underlying user folder must support editing users via the usual Zope API.
        Passwords for groups seem to be currently irrelevant in GRUF."""

    def test_removeGroups(self, ):
        """Remove the group in the provided list (if possible).

        Will by default remove this group's GroupWorkspace if it exists. You may
        turn this off by specifying keep_workspaces=true.
        Underlying user folder must support removing users via the usual Zope API."""

    def test_setGroupOwnership(self, ):
        """Make the object 'object' owned by group 'group' (a portal_groupdata-ish object)"""

    def test_setGroupWorkspacesFolder(self, ):
        """ Set the location of the Group Workspaces folder by id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders.

        If anyone really cares, we can probably make the id work as a path as well,
        but for the moment it's only an id for a folder in the portal root, just like the
        corresponding MembershipTool functionality. """

    def test_getGroupWorkspacesFolderId(self, ):
        """ Get the Group Workspaces folder object's id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """

    def test_getGroupWorkspacesFolder(self, ):
        """ Get the Group Workspaces folder object.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """

    def test_toggleGroupWorkspacesCreation(self, ):
        """ Toggles the flag for creation of a GroupWorkspaces folder upon first
        use of the group. """

    def test_getGroupWorkspacesCreationFlag(self, ):
        """Return the (boolean) flag indicating whether the Groups Tool will create a group workspace
        upon the next use of the group (if one doesn't exist). """

    def test_getGroupWorkspaceType(self, ):
        """Return the Type (as in TypesTool) to make the GroupWorkspace."""

    def test_setGroupWorkspaceType(self, ):
        """Set the Type (as in TypesTool) to make the GroupWorkspace. Expects the name of a Type."""

    def test_createGrouparea(self, ):
        """Create a space in the portal for the given group, much like member home
        folders."""

    def test_getGroupareaFolder(self, ):
        """Returns the object of the group's work area."""

    def test_getGroupareaURL(self, ):
        """Returns the full URL to the group's work area."""


    
class TestGroupDataTool(GroupTestCase, testInterface.TestInterface):
    klasses = (        # tell which classes to check
        GroupDataTool.GroupDataTool,
        )
    ignore_interfaces = (
        ActionProviderBase.__implements__,
        )

    

    def test_wrapGroup(self,):
        """Test group wrapping"""
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(g1.__class__.__name__, "GroupData")
        self.failUnlessEqual(g1.getGroupName(), "g1")
        g1 = self.groups.getGroupById("group_g1")
        self.failUnlessEqual(g1.__class__.__name__, "GroupData")
        self.failUnlessEqual(g1.getGroupName(), "g1")




class TestGroupData(GroupTestCase, testInterface.TestInterface):
    klasses = (        # tell which classes to check
        GroupDataTool.GroupData,
        )
    ignore_interfaces = (
        ActionProviderBase.__implements__,
    )

    
    def test_setProperties(self, properties = None, **kw):
        """We set some properties on groups
        """
        g = self.groups.getGroupById("g1")

        # Regular property setting
        g.setProperties({
            "email": "test@toto.com",
            "description": "azer",
            })
        self.failUnlessEqual(g.getProperty("email"), "test@toto.com", )
        self.failUnlessEqual(g.getProperty("description"), "azer", )
        
        # Keyword property setting
        g.setProperties(email = "other@toto.com", description = "Bloub.")
        self.failUnlessEqual(g.getProperty("email"), "other@toto.com", )
        self.failIfEqual(g.getProperty("name"), "Bloub.")

        # The Hacky Touch
        g.setProperties(id = "INVALID")
        self.failIfEqual(g.getProperty("id"), "g1")


    def test_getProperty(self,):
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(g1.getProperty("name"), "g1")


    def test_getProperties(self,):
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(
            g1.getProperties(),
            {"email": "", "description": "", "title": ""},
            )
        g1.setProperties(email = "test@toto.com", description = "marih", title = "Hello")
        self.failUnlessEqual(
            g1.getProperties(),
            {
            "email": "test@toto.com",
            "description": "marih",
            "title": "Hello",
            },
            )

    def test_getGroupId(self,):
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(g1.getGroupId(), "g1")

    def test_getGroupName(self,):
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(g1.getGroupName(), "g1")

    def test_getGroupMembers(self,):
        g1 = self.groups.getGroupById("g1")
        members = map(lambda x: x.getMemberId(), g1.getGroupMembers())
        members.sort()
        self.failUnlessEqual(
            members,
            ["u2", "u3", "u4", ]
            )

    def test_getGroupMemberIds(self,):
        g1 = self.groups.getGroupById("g1")
        members = g1.getGroupMemberIds()
        members.sort()
        self.failUnlessEqual(
            members,
            ["u2", "u3", "u4", ]
            )

    def test_addMember(self,):
        g1 = self.groups.getGroupById("g1")

        # Valid user
        g1.addMember("u1")
        members = g1.getGroupMemberIds()
        members.sort()
        self.failUnlessEqual(
            members,
            ["u1", "u2", "u3", "u4", ]
            )

        # Invalid user
        self.failUnlessRaises(
            ValueError,
            g1.addMember,
            "bloubbloub",
            )

    def test_removeMember(self,):
        g1 = self.groups.getGroupById("g1")

        # Valid user
        g1.removeMember("u2")
        members = g1.getGroupMemberIds()
        members.sort()
        self.failUnlessEqual(
            members,
            ["u3", "u4", ]
            )

        # Invalid user
        self.failUnlessRaises(
            ValueError,
            g1.removeMember,
            "bloubbloub",
            )

    def test_getGroup(self,):
        g1 = self.groups.getGroupById("g1")
        self.failUnlessEqual(
            g1.getGroup().__class__.__name__,
            "GRUFGroup",
            )



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupsTool))
        suite.addTest(unittest.makeSuite(TestGroupDataTool))
        suite.addTest(unittest.makeSuite(TestGroupData))
        return suite

