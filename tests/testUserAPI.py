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
from Products.GroupUserFolder import GRUFUser
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')

import GRUFTestCase
import testInterface
from Log import *


class TestUserFolderAPI(GRUFTestCase.GRUFTestCase, testInterface.TestInterface):

    klasses = (        # tell which classes to check
        GRUFUser.GRUFUser,
        GRUFUser.GRUFGroup,
        )

    def test03ClassSecurityInfo(self,):
        """We inhibit this test: class security info is not managed this way with user objects
        """
        pass
    
    def test_getId(self,):
        u = self.gruf.getUser("u1")
        self.failUnless(u.getId() == "u1")
        u = self.gruf.getUser("group_g1")
        self.failUnless(u.getId() == "group_g1")

    def test_getUserName(self,):
        u = self.gruf.getUser("u1")
        self.failUnless(u.getUserName() == "u1")
        u = self.gruf.getUser("group_g1")
        self.failUnless(u.getUserName() == "g1")

    def test_getName(self,):
        u = self.gruf.getUser("u1")
        self.failUnless(u.getUserName() == "u1")
        u = self.gruf.getUser("group_g1")
        self.failUnless(u.getUserName() == "g1")

    def test_getRoles(self):
        u = self.gruf.getUser("u5")
        r = list(u.getRoles())
        r.sort()
        Log(LOG_DEBUG, r)
        self.failUnless(r == ["Authenticated", "r1", "r2", ])

    def test_setRoles(self,):
        # Initial situation
        u = self.gruf.getUser("u5")
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", ])

        # Regular role setting
        u.setRoles(["r3", "r2", "r1"])
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", "r3"])

        # Try to add an invalid role => should be prohibited
        try:
            u.setRoles(["r3", "r2", "r1", "bloub"])
        except ValueError:
            pass
        else:
            raise AssertionError, "Should raise a ValueError here"

        # Reset roles : we must keep group-defined roles
        u.setRoles([])
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", ])

        # Now reset roles on another user
        u = self.gruf.getUser("u6")
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", ])
        u.setRoles([])
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r2", ])

    def test_addRole(self,):
        # Initial situation
        u = self.gruf.getUser("u5")
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", ])

        # Regular role adding
        u.addRole("r3", )
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", "r3"])

        # Invalid role adding -> should raise
        try:
            u.addRole("bloub", )
        except ValueError:
            pass
        else:
            raise AssertionError, "Should raise a ValueError here"

    def test_removeRole(self,):
        # Initial situation
        u = self.gruf.getUser("u6")
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r1", "r2", ])

        # Regular role removing
        u.removeRole("r1", )
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r2", ])

        # Try to remove a non-used role => should be transparent
        u.removeRole("r1", )
        r = list(u.getRoles())
        r.sort()
        self.failUnless(r == ["Authenticated", "r2", ])

        # Remove group role : we must keep group-defined roles
        u.removeRole("r2")
        r = list(u.getRoles())
        r.sort()
        Log(LOG_DEBUG, r)
        self.failUnless(r == ["Authenticated", "r2", ])

    def test_getRolesInContext(self, ):
        r = self.gruf.getUser("u2").getRolesInContext(self.gruf_folder.lr)
        self.failUnless("r3" in r)
        r = self.gruf.getUser("u3").getRolesInContext(self.gruf_folder.lr)
        self.failUnless("r1" in r)
        self.failUnless("r3" in r)

    def test_has_permission(self, ):
        pass            # Don't know how to test this :(

    def test_allowed(self, ):
        pass            # XXX Will have to test that intensively !

    def test_has_role(self, ):
        u = self.gruf.getUser("u2")
        self.failUnless(u.has_role("r3", self.gruf_folder.lr, ))

    def test_isGroup(self, ):
        u = self.gruf.getUser("u1")
        self.failUnless(not u.isGroup())
        u = self.gruf.getUser("u2")
        self.failUnless(not u.isGroup())
        u = self.gruf.getUser("g1")
        self.failUnless(u.isGroup())
        u = self.gruf.getUser("ng2")
        self.failUnless(u.isGroup())
        u = self.gruf.getUser("g3")
        self.failUnless(u.isGroup())
        

    def test_getGroupNames(self,):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getGroupNames()
        g.sort()
        self.failUnless(g == ["g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getGroupNames()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getGroupNames()
        g.sort()
        self.failUnless(g == ["g1", ])

        # Non-transitivity test
        u = self.gruf.getUser("u10")
        g = u.getGroupNames()
        g.sort()
        self.failUnless(g == ["ng2", "ng3", ])

    def test_getGroupIds(self, ):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getGroupIds()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getGroupIds()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getGroupIds()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Non-transitivity test
        u = self.gruf.getUser("u10")
        g = u.getGroupIds()
        g.sort()
        self.failUnless(g == ["group_ng2", "group_ng3", ])

    def test_getGroups(self, ):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getGroups()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getGroups()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getGroups()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Transitivity test
        u = self.gruf.getUser("u10")
        g = u.getGroups()
        g.sort()
        self.failUnless(g == ["group_g2", "group_g3", "group_ng2", "group_ng3", ])


    def test_getImmediateGroups(self,):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getImmediateGroups()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getImmediateGroups()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getImmediateGroups()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Transitivity test
        u = self.gruf.getUser("u10")
        g = u.getImmediateGroups()
        g.sort()
        self.failUnless(g == ["group_ng2", "group_ng3", ], u.getImmediateGroups())


    def test_getAllGroupIds(self):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getAllGroupIds()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getAllGroupIds()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getAllGroupIds()
        g.sort()
        self.failUnless(g == ["group_g1", ])

        # Transitivity test
        u = self.gruf.getUser("u10")
        g = u.getAllGroupIds()
        g.sort()
        self.failUnless(g == ["group_g2", "group_g3", "group_ng2", "group_ng3", ])


    def test_getAllGroupNames(self):
        # Regular test
        u = self.gruf.getUser("u2")
        g = u.getAllGroupNames()
        g.sort()
        self.failUnless(g == ["g1", ])

        # Empty list test
        u = self.gruf.getUser("u1")
        g = u.getAllGroupNames()
        g.sort()
        self.failUnless(g == [])

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        g = u.getAllGroupNames()
        g.sort()
        self.failUnless(g == ["g1", ])

        # Transitivity test
        u = self.gruf.getUser("u10")
        g = u.getAllGroupNames()
        g.sort()
        self.failUnless(g == ["g2", "g3", "ng2", "ng3", ])


    def test_isInGroup(self, ):
        u = self.gruf.getUser("u2")
        self.failUnless(u.isInGroup("group_g1", ))
        self.failUnless(not u.isInGroup("g1", ))        # We don not allow group names

        # Empty list test
        u = self.gruf.getUser("u1")
        self.failUnless(not u.isInGroup("group_g1", ))

        # GroupOfGroup test
        u = self.gruf.getUser("ng1")
        self.failUnless(u.isInGroup("group_g1", ))

        # Transitivity test
        u = self.gruf.getUser("u10")
        self.failUnless(u.isInGroup("group_g2", ))
        self.failUnless(u.isInGroup("group_g3", ))
        self.failUnless(u.isInGroup("group_ng2", ))
        self.failUnless(u.isInGroup("group_ng3", ))
        

    def test_setGroups(self, ):
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = [],
            )
        u = self.gruf.getUser("created_user")
        u.setGroups(["g1", "g2", ], )
        self.compareGroups("created_user", ["g1", "g2", ], )
        u.setGroups([], )
        self.compareGroups("created_user", [], )
        u.setGroups(["group_g1", "group_g2", ], )
        self.compareGroups("created_user", ["g1", "g2", ], )
        try:
            u.setGroups(["group_g1", "group_g2", "bloub", ], )
        except ValueError:
            pass
        else:
            raise AssertionError, "Should raise ValueError"

    def test_addGroup(self, ):
        u = self.gruf.getUser("u1")
        self.failUnless(u.getGroups() == [])
        u.addGroup("g3")
        self.failUnless(u.getGroups() == ["group_g3"])
        u.addGroup("group_g2")
        r = u.getGroups()
        r.sort()
        self.failUnless(r == ["group_g2", "group_g3"])
        

    def test_removeGroup(self, ):
        u = self.gruf.getUser("u1")
        u.addGroup("group_g3")
        u.addGroup("group_g2")
        r = u.getGroups()
        r.sort()
        self.failUnless(r == ["group_g2", "group_g3"])
        u.removeGroup("group_g3")
        Log(LOG_DEBUG, u.getGroups())
        self.failUnless(u.getGroups() == ["group_g2", ])
        u.removeGroup("group_g2")
        self.failUnless(u.getGroups() == [])
        
        
    def test_getRealId(self, ):
        u = self.gruf.getUser("u1")
        self.failUnless(u.getRealId() == "u1")
        u = self.gruf.getUser("g1")
        self.failUnless(u.getRealId() == "g1")
        u = self.gruf.getUser("group_g1")
        self.failUnless(u.getRealId() == "g1")
        

    def test_getDomains(self,):
        """Return the list of domain restrictions for a user"""
        self.gruf.userFolderAddUser("test_crea", "secret", [], ["a", 'b', 'c'], [])
        u = self.gruf.getUser("test_crea")
        d = list(u.getDomains())
        d.sort()
        self.failUnless(d == ["a", "b", "c", ])

    
    def test_setPassword(self):
        # Regular user password
        user = self.gruf.getUser('u1')
        self.failUnless(user.authenticate('secret', self.app.REQUEST))
        user.setPassword("marih")
        self.failUnless(not user.authenticate('secret', self.app.REQUEST))
        self.failUnless(user.authenticate('marih', self.app.REQUEST))

        # Prohibit group password changing (the method shouldn't even be available)
        u = self.gruf.getUser("g1")
        try:
            u.setPassword("bloub")
        except AttributeError:
            pass                # Ok
        else:
            raise AssertionError, "Password change must be prohibited for groups"

    def test_setDomains(self, ):
        u = self.gruf.getUser("u1")
        self.failUnless(not u.getDomains())
        u.setDomains(["d1", "d2", "d3", ])
        d = list(u.getDomains())
        d.sort()
        self.failUnless(d == ["d1", "d2", "d3", ])
        u.setDomains([])
        self.failUnless(tuple(u.getDomains()) == ())
        u.setDomains(["xxx"])
        self.failUnless(tuple(u.getDomains()) == ("xxx", ))
        

    def test_addDomain(self, ):
        "..."

    def test_removeDomain(self, ):
        "..."

    def test_getMemberIds(self, ):
        u = self.gruf.getGroup("ng2")
        ulist = u.getMemberIds()
        ulist.sort()
        self.failUnless(ulist == ['group_ng3', 'group_ng4', 'group_ng5', 'u10', 'u11', 'u9', ])

    def test_getUserMemberIds(self, ):
        u = self.gruf.getGroup("ng2")
        ulist = u.getUserMemberIds()
        ulist.sort()
        self.failUnless(ulist == ['u10', 'u11', 'u9', ])

        u = self.gruf.getGroup("g2")
        ulist = u.getUserMemberIds()
        ulist.sort()
        self.failUnless(ulist == ['u10', 'u11', 'u3', 'u4', 'u5', 'u9', ])

    def test_getGroupMemberIds(self, ):
        u = self.gruf.getGroup("ng2")
        ulist = u.getGroupMemberIds()
        ulist.sort()
        self.failUnless(ulist == ['group_ng3', 'group_ng4', 'group_ng5'])

    def test_hasMember(self, ):
        self.failUnless(self.gruf.getGroup("g2").hasMember("u4"))
        self.failUnless(self.gruf.getGroup("g2").hasMember("group_ng2"))

    def test_addMember(self, ):
        g = self.gruf.getGroup("ng3")
        self.failUnless("u1" not in g.getMemberIds())
        g.addMember("u1")
        self.failUnless("u1" in g.getMemberIds())
        # 'Will have to test with groups as well
         
    def test_removeMember(self, ):
        g = self.gruf.getGroup("ng3")
        self.failUnless("u1" not in g.getMemberIds())
        g.addMember("u1")
        self.failUnless("u1" in g.getMemberIds())
        g.removeMember("u1")
        self.failUnless("u1" not in g.getMemberIds())
        # 'Will have to test with groups as well



    def test_getProperty(self,):
        """Will raise for regular user folders
        """
        try:
            self.gruf.getUser("u1").getProperty("email")
        except:
            pass
        else:
            raise AssertionError, "Should raise"

    def test_hasProperty(self,):
        self.failUnless(not self.gruf.getUser("u1").hasProperty("email"))

    def test_setProperty(self,):
        try:
            self.gruf.getUser("u1").setProperty("email", "test@test.com")
        except NotImplementedError:
            pass
        else:
            raise AssertionError, "Should raise here."



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestUserFolderAPI))
        return suite

