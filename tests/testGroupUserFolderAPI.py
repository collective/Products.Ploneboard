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
from Products.GroupUserFolder.interfaces import IUserFolder
from Products.GroupUserFolder import GroupUserFolder
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')

import GRUFTestCase
import testInterface
from Log import *


class TestGroupUserFolderAPI(GRUFTestCase.GRUFTestCase, testInterface.TestInterface):


    klasses = (        # tell which classes to check
        GroupUserFolder.GroupUserFolder,
        )

    def test10GRUFMethods(self,):
        """
        We test that GRUF's API is well protected
        """
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')

    #                                                   #
    #                  GRUF API testing                 #
    #                                                   #

        
    def test_getUserNames(self):
        un = self.gruf.getUserNames()
        users = [
            'g1', 'g2', "g3", "g4",
            "ng1", "ng2", "ng3", "ng4", "ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "extranet", "intranet", "compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))


    def test_getUserIds(self):
        un = self.gruf.getUserIds()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))
                
    def test_getUser(self):
        # Check id access
        usr = self.gruf.getUser("u1")
        self.failUnless(usr.__class__.__name__ == "GRUFUser")
        self.failUnless(usr.getUserName() == "u1")
        grp = self.gruf.getUser("group_g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")

        # Check name access for groups
        grp = self.gruf.getUser("g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")

    def test_getUsers(self):
        objects = self.gruf.getUsers()
        un = map(lambda x: x.getId(), objects)
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getUserById(self):
        # Check user & group access
        self.failUnless(self.gruf.getUserById("u1").getUserName() == "u1")
        self.failUnless(self.gruf.getUserById("group_g1").getId() == "group_g1")

        # Prohibit direct group access
        self.failUnless(self.gruf.getUserById("g1", default = None) is None)

        # check exception raising & default values
        try: self.gruf.getUserById("ZORGLUB")
        except ValueError: pass
        else: raise "AssertionError", "Should raise"
        self.failUnless(self.gruf.getUserById("ZORGLUB", default = "bla") == "bla")

    def test_getUserByName(self):
        # Check user & group access
        self.failUnless(self.gruf.getUserByName("u1").getUserName() == "u1")
        self.failUnless(self.gruf.getUserByName("g1").getId() == "group_g1")

        # Check group id access
        self.failUnless(self.gruf.getUserByName("group_g1", None).getId() == "group_g1")

        # Check exception raising
        try: self.gruf.getUserByName("ZORGLUB")
        except ValueError: pass
        else: raise "AssertionError", "Should raise"
        self.failUnless(self.gruf.getUserByName("ZORGLUB", default = "bla") == "bla")


    # User access

    def test_getPureUserNames(self):
        """Same as getUserNames() but without groups
        """
        un = self.gruf.getPureUserNames()
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getPureUserIds(self,):
        """Same as getUserIds() but without groups
        """
        un = self.gruf.getPureUserIds()
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getPureUsers(self):
        """Same as getUsers() but without groups.
        """
        # Fetch pure users
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        objects = self.gruf.getPureUsers()
        un = map(lambda x: x.getId(), objects)
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u, ))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))


    def test_getPureUser(self,):
        u = self.gruf.getPureUser("u1")
        self.failUnless(u)
        u = self.gruf.getPureUser("g1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("group_g1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("group_u1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("u4")
        self.failUnless(u)
        
    # Group access

    def test_getGroupNames(self):
        """Same as getUserNames() but without pure users.
        """
        un = self.gruf.getGroupNames()
        users = [
            'g1', 'g2', "g3", "g4",
            "ng1", "ng2", "ng3", "ng4", "ng5",
            "extranet", "intranet", "compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getGroupIds(self,):
        un = self.gruf.getGroupIds()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))


    def test_getGroups(self):
        objects = self.gruf.getGroups()
        un = map(lambda x: x.getId(), objects)
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getGroup(self):
        # Check name access
        grp = self.gruf.getGroup("g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.getId() == "group_g1")

        # Check id access
        grp = self.gruf.getGroup("group_g1")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")

        # Prevent user access
        usr = self.gruf.getGroup("u1")
        self.failUnless(usr is None)

    def test_getGroupById(self):
        # Id access
        grp = self.gruf.getGroupById("group_g1")
        self.failUnless(grp.getId() == "group_g1")

        # Prevent name access
        grp = self.gruf.getGroupById("g1", default = None)
        self.failUnless(grp is None)

        # Prevent user access
        grp = self.gruf.getGroupById("u1", default = None)
        self.failUnless(grp is None)

        # Check raise if user/group not found
        try: self.gruf.getGroupById("ZORGLUB")
        except ValueError: pass
        else: raise "AssertionError", "Should raise"
        self.failUnless(self.gruf.getGroupById("ZORGLUB", default = "bla") == "bla")

    def test_getGroupByName(self):
        # Name access
        grp = self.gruf.getGroupByName("g1")
        self.failUnless(grp.getId() == "group_g1")

        # Allow id access
        grp = self.gruf.getGroupByName("group_g1", default = None)
        self.failUnless(grp.getId() == "group_g1")

        # Prevent user access
        self.failUnless(self.gruf.getGroupByName("u1", default = None) is None)

        # Check raise if user/group not found
        try: self.gruf.getGroupByName("ZORGLUB")
        except ValueError: pass
        else: raise "AssertionError", "Should raise"
        self.failUnless(self.gruf.getGroupByName("ZORGLUB", default = "bla") == "bla")


    # Mutators

    def test_userFolderAddUser(self):
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getUser("created_user"))
        self.gruf.userFolderAddUser(
            name = "group_test_prefix",
            password = "secret",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getUser("group_test_prefix"))
        self.failIf(self.gruf.getUser("group_test_prefix").isGroup())
        
    def test_userFolderEditUser(self):
        self.gruf.userFolderEditUser(
            name = "u1",
            password = "secret2",
            roles = ["r1", ],
            groups = ["g1", ],
            )
        self.compareRoles(None, "u1", ['r1',], )

    def test_userFolderDelUsers(self):
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderDelUsers(['created_user', ])
        self.failUnless(self.gruf.getUser("created_user") is None)

    def test_userFolderAddGroup(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getGroup("created_group"))
        self.gruf.userFolderAddGroup(
            name = "group_test_prefix",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getGroup("group_test_prefix"))
        self.failUnless(self.gruf.getGroup("group_test_prefix").isGroup())

        # Prevent group_group_xxx names
        self.failUnless(self.gruf.getGroupById("group_group_test_prefix", None) is None)
        
    def test_userFolderEditGroup(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderEditGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = ["group_g1", ],
            )
        self.compareRoles(None, "created_group", ['r1',], )
        self.failUnless(
            "g1" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )
        self.gruf.userFolderEditGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = ["g2", ],
            )
        self.failUnless(
            "g2" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )

    def test_userFolderDelGroups(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderDelGroups(['created_group', ])
        self.failUnless(self.gruf.getGroup("created_group") is None)


    # User mutation

    def test_userSetRoles(self):
        self.gruf.userSetRoles("u1", ["r1", "r2", ], )
        self.compareRoles(None, "u1", ["r1", "r2", ], )
        self.gruf.userSetRoles("u1", [], )
        self.compareRoles(None, "u1", [], )

    def test_userAddRole(self):
        self.gruf.userAddRole("u1", "r1", )
        self.gruf.userAddRole("u1", "r2", )
        self.compareRoles(None, "u1", ["r1", "r2", ], )

    def test_userRemoveRole(self):
        """Remove the role of a user atom
        """
        self.gruf.userSetRoles("u1", ["r1", "r2", ], )
        self.compareRoles(None, "u1", ["r1", "r2", ], )
        self.gruf.userRemoveRole("u1", "r1", )
        self.compareRoles(None, "u1", ["r2", ], )

    def test_userSetPassword(self):
        """Test user password setting
        """
        # Regular user password
        user = self.gruf.getUser('u1')
        self.failUnless(self.gruf.authenticate("u1", 'secret', self.app.REQUEST))
        self.gruf.userSetPassword("u1", "bloub")
        user = self.gruf.getUser('u1')
        self.failUnless(not self.gruf.authenticate("u1", 'secret', self.app.REQUEST))
        self.failUnless(self.gruf.authenticate("u1", 'bloub', self.app.REQUEST))

        # Group password changing must fail
        try: self.gruf.userSetPassword("g1", "bloub")
        except ValueError: pass                # ok
        else: raise "AssertionError", "Should raise"
        try: self.gruf.userSetPassword("group_g1", "bloub")
        except ValueError: pass                # ok
        else: raise "AssertionError", "Should raise"

    def test_userGetDomains(self):
        ""

    def test_userSetDomains(self):
        ""
        u = self.gruf.getUser("u1")
        self.failUnless(not self.gruf.userGetDomains("u1"))
        self.gruf.userSetDomains("u1", ["d1", "d2", "d3", ])
        self.failUnless(self.gruf.userGetDomains("u1") == ("d1", "d2", "d3", ))
        self.gruf.userSetDomains("u1", [])
        self.failUnless(self.gruf.userGetDomains("u1") == ())
        self.gruf.userSetDomains("u1", ["xxx"])
        self.failUnless(self.gruf.userGetDomains("u1") == ("xxx", ))

    def test_userAddDomain(self):
        ""

    def test_userRemoveDomain(self):
        ""

    def test_userSetGroups(self):
        # Test user
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = [],
            )
        self.gruf.userSetGroups("created_user", ["g1", "g2", ], )
        self.compareGroups("created_user", ["g1", "g2", ], )
        self.gruf.userSetGroups("created_user", [], )
        self.compareGroups("created_user", [], )

    def test_userAddGroup(self):
        # Test user
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = ["g2", ],
            )
        self.gruf.userAddGroup("created_user", "g1", )
        self.compareGroups("created_user", ["g1", "g2", ], )

    def test_userRemoveGroup(self):
        """Remove the group of a user atom
        """
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = ["g2", "g1", ],
            )
        self.gruf.userRemoveGroup("created_user", "g1", )
        self.compareGroups("created_user", ["g2", ], )


    # Security management

    def test_setRolesOnUsers(self):
        """Set a common set of roles for a bunch of user atoms.
        """
        self.gruf.setRolesOnUsers(["r1", "r2", "r3", ], ["u1", "u2", ])
        self.compareRoles(None, "u1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "u2", ["r1", "r2", "r3", ])
        self.gruf.setRolesOnUsers([], ["u2", ])
        self.compareRoles(None, "u1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "u2", [])

    def test_setRolesOnGroups(self,):
        """Same as test_setRolesOnUsers but with groups"""
        self.gruf.setRolesOnUsers(["r1", "r2", "r3", ], ["g1", "g2", ])
        self.compareRoles(None, "g1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "g2", ["r1", "r2", "r3", ])

    def test_getUsersOfRole(self):
        should_be = [
            'group_ng2','group_ng3',
            'group_ng4',
            'group_ng5',
            'u9',
            'u5',
            'u4',
            'u7',
            'u6',
            'u11',
            'u10',
            'group_g3',
            'group_g4',
            ]
        should_be.sort()
        users = list(self.gruf.getUsersOfRole("r2"))
        users.sort()
        self.failUnless(users == should_be, (should_be, users, ))

    def test_getRolesOfUser(self):
        self.failUnless("r1" in self.gruf.getRolesOfUser("u3"), self.gruf.getRolesOfUser("u3"), )

    def test_userFolderGetRoles(self,):
        """
        Test existing roles
        """
        should_be =  [
            'Anonymous',
            'Authenticated',
            'Manager',
            'Owner',
            'r1',
            'r2',
            'r3',
            'test_role_1_',
            ]
        should_be.sort()
        roles = list(self.gruf.userFolderGetRoles())
        roles.sort()
        self.failUnless(roles == should_be)

    def test_userFolderAddRole(self):
        self.gruf.userFolderAddRole("r9")
        self.failUnless(
            "r9" in self.gruf.userFolderGetRoles(),
            )

    def test_userFolderDelRoles(self):
        """Delete roles.
        The removed roles will be removed from the UserFolder's users and groups as well,
        so this method can be very time consuming with a large number of users.
        """
        # Add a role and set it to a few groups
        self.gruf.userFolderAddRole("r9")
        self.failUnless(
            "r9" in self.gruf.userFolderGetRoles(),
            )
        self.gruf.userAddRole("g2", "r9")
        self.gruf.userAddRole("u1", "r9")
        self.failUnless(
            "r9" in self.gruf.getRolesOfUser("u1")
            )
        self.failUnless(
            "r9" in self.gruf.getRolesOfUser("u4")
            )

        # Now, remove it
        self.gruf.userFolderDelRoles(['r9', ])
        self.failUnless(
            "r9" not in self.gruf.getRolesOfUser("u1")
            )
        self.failUnless(
            "r9" not in self.gruf.getRolesOfUser("u4")
            )
        

    # Groups support
    def test_setMembers(self):
        """Set the members of the group
        """

    def test_getMemberIds(self,):
        should_be = [
            'group_ng2',
            'group_ng3',
            'group_ng4',
            'group_ng5',
            'u9',
            'u5',
            'u4',
            'u6',
            'u11',
            'u10',
            ]
        should_be.sort()
        users = list(self.gruf.getMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be))


    def test_getUserMemberIds(self,):
        """This tests nested groups"""
        should_be = [
            'u9',
            'u5',
            'u4',
            'u6',
            'u11',
            'u10',
            ]
        should_be.sort()
        users = list(self.gruf.getUserMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be, ))
        
    def test_getGroupMemberIds(self,):
        should_be = [
            'group_ng2',
            'group_ng3',
            'group_ng4',
            'group_ng5',
            ]
        should_be.sort()
        users = list(self.gruf.getGroupMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be, ))


    def test_addMember(self):
        """Add a member to a group
        """
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless("u1" in self.gruf.getMemberIds("ng3"))


    def test_removeMember(self):
        """Remove a member from a group
        """    
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless("u1" in self.gruf.getMemberIds("ng3"))
        self.gruf.removeMember("ng3", "u1")
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))
        

    def test_hasMember(self,):
        self.failUnless(not self.gruf.hasMember("ng3", "u1"))
        self.failUnless(not self.gruf.hasMember("group_ng3", "u1"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless(self.gruf.hasMember("ng3", "u1"))
        self.failUnless(self.gruf.hasMember("group_ng3", "u1"))
        self.gruf.removeMember("ng3", "u1")
        self.failUnless(not self.gruf.hasMember("ng3", "u1"))
        self.failUnless(not self.gruf.hasMember("group_ng3", "u1"))
        

    # Misc
    def test_getRealId(self,):
        """Test group id without group prefix"""
        g = self.gruf.getUser("group_ng2")
        self.failUnless(g.getRealId() == "ng2")
        u = self.gruf.getUser("u1")
        self.failUnless(u.getRealId() == "u1")



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupUserFolderAPI))
        return suite

