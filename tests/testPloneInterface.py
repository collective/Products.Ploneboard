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

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

# Start the web server
host, port = ZopeTestCase.utils.startZServer(4)
base = 'http://%s:%d/%s' %(host, port, ZopeTestCase._folder_name)

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')


# Set log options if Log module is available
# This is done to set LOG_PROCESSORs to file logs instead of Zope logs
try:
    import Log

    Log.LOG_LEVEL = Log.LOG_DEBUG

    Log.LOG_PROCESSOR = {
        Log.LOG_NONE: Log.logFile,
        Log.LOG_CRITICAL: Log.logFile,
        Log.LOG_ERROR: Log.logFile,
        Log.LOG_WARNING: Log.logFile,
        Log.LOG_NOTICE: Log.logFile,
        Log.LOG_DEBUG: Log.logFile,
        }

    from Log import *
    Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))

except:
    print "Log module not available"
    LOG_DEBUG = None
    LOG_NOTICE = None
    LOG_WARNING = None
    LOG_ERROR = None
    LOG_CRITICAL = None
    def Log(*args, **kw):
        pass
    raise



class ManagementOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('manager', 'secret')

class UnauthorizedOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        raise Unauthorized, 'The URLopener was asked for authentication'


class TestPloneInterface(PloneTestCase.PloneTestCase):

    def afterSetUp(self,):
        self.loginPortalOwner()
        self.qi = self.portal.portal_quickinstaller
        self.qi.installProduct('GroupUserFolder')
        self.mt = self.portal.portal_membership
        self.gt = self.portal.portal_groups
        self.acl_users = self.portal.acl_users

    def testUserCreation(self,):
        """
        test user creation with plone
        """
        # Create a non-group-related user
        self.mt.addMember("member1", "secret", ['Member',], None)
        self.failUnless("member1" in self.acl_users.getUserNames())
        self.failUnless("Member" in self.acl_users.getUser("member1").getRoles())

    def testGroupCreation(self,):
        """
        test group creation with plone
        """
        # Group without roles
        self.gt.addGroup("group1", roles = ['Member',], )
        self.failUnless("group_group1" in self.acl_users.getGroupNames())
        self.failUnless("Member" in self.acl_users.getGroup("group_group1").getRoles())

        # Group with valid roles
        self.portal._addRole('SampleRole')
        self.gt.addGroup("group2", roles = ['SampleRole',], )
        self.failUnless("SampleRole" in self.acl_users.getGroup("group_group2").getRoles())
        self.failUnless("Member" not in self.acl_users.getGroup("group_group2").getRoles())

    def testUserToGroup(self,):
        """
        test user and group interaction with Plone API
        """
        # Add a user and a group with valid roles
        self.portal._addRole('SampleRole')
        self.gt.addGroup("group2", roles = ['SampleRole',], )
        self.mt.addMember("member1", "secret", ['Member',], None)

        # test group affectation
        group = self.gt.getGroupById("group2")
        group.addMember("member1")
        Log(LOG_DEBUG, group.getGroupMemberIds())
        self.failUnless("member1" in group.getGroupMemberIds())

    def testUserToGroupRoles(self,):
        # Add a user and a group with valid roles
        self.portal._addRole('SampleRole')
        self.gt.addGroup("group2", roles = ['SampleRole',], )
        self.mt.addMember("member1", "secret", ['Member',], None)
        group = self.gt.getGroupById("group2")
        group.addMember("member1")

        # test roles
        self.failUnless("SampleRole" in self.acl_users.getUser("member1").getRoles())
        self.failUnless("Member" in self.acl_users.getUser("member1").getRoles())

        # Ensure that "group-acquired" role is not affected to the user directly
        self.failUnless("SampleRole" not in self.acl_users.getUser("member1").getUserRoles())


    def testUserToGroupRolesBug(self,):
        # Try to reproduce a bug happening when you affect twice the same user
        # to the same group: in this case, the user will get group's role affected
        # to him directly... which should not happend.
        # Add a user and a group with valid roles
        self.portal._addRole('SampleRole')
        self.gt.addGroup("group2", roles = ['SampleRole',], )
        self.mt.addMember("member1", "secret", ['Member',], None)
        group = self.gt.getGroupById("group2")
        group.addMember("member1")

        # Do it once again
        group.addMember("member1")

        # Ensure that "group-acquired" role is not affected to the user directly
        self.failIf("SampleRole" in self.acl_users.getUser("member1").getUserRoles())

    def testUserToGroupRemoving(self,):
        # Add a user and a group with valid roles
        self.portal._addRole('SampleRole')
        self.gt.addGroup("group2", roles = ['SampleRole',], )
        self.mt.addMember("member1", "secret", ['Member',], None)
        group = self.gt.getGroupById("group2")
        group.addMember("member1")

        # Remove user from the group and check if everything still works
        group.removeMember("member1")
        self.failUnless("member1" not in group.getGroupMembers())
        self.failUnless("SampleRole" not in self.acl_users.getUser("member1").getRoles())
        self.failUnless("Member" in self.acl_users.getUser("member1").getRoles())


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneInterface))
        return suite
