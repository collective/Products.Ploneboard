import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFMember.tests import CMFMemberTestCase

""" Test member creation from users, management of user properties through
member interface."""

class TestUser(CMFMemberTestCase.CMFMemberTestCase):

    def testChangeUserProperties(self):
        portal = self.getPortal()
        member = self.membership.getMemberById(self.portal_user.getUserName())
        password2 = 'password2'
        member._setPassword(password2)
        self.assertEqual(member.getPassword(), password2)
        member.setRoles('Member, Manager')
#       XXX - the current getRoles method filters out roles not available to
#       the member's user's acl_users folder.  I'm not sure if that's the best
#       approach -- maybe we should allow any portal roles?  OTOH, that creates
#       the problem of having different portals all assigning different roles
#       to the same user.
        self.failUnless(self.compareTuples(member.getRoles(), ('Member', 'Manager', 'Authenticated')))
        member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(member.getDomains(), ('127.0.0.1', '127.0.0.2'))


    def testChangeUserPropertiesRoot(self):
        portal = self.getPortal()
        newSecurityManager(None, self.root_user)
        member = portal.portal_membership.getAuthenticatedMember()
        password2 = 'password2'
        member._setPassword(password2)
        self.assertEqual(member.getPassword(), password2)
        member.setRoles('Manager, Owner')
        self.failUnless(self.compareTuples(member.getRoles(), ('Manager', 'Owner', 'Authenticated')))
        member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(member.getDomains(), ('127.0.0.1', '127.0.0.2'))

    def testWrapUser(self):
        portal = self.getPortal()

        # first create the user as an administrator
        member = self.membership.getMemberById(self.portal_user.getUserName())        
        
        newSecurityManager(None, self.portal_user)
        member = portal.portal_membership.getAuthenticatedMember()

        # make sure all the member properties we set are correct
        self.failUnless(member != None)
        self.assertEqual(member.getId(), self.portal_user_info['id'])
        self.assertEqual(member.getPassword(), self.portal_user_info['password'])
        self.failUnless(self.compareTuples(member.getRoles(), self.portal_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(member.getDomains(), self.portal_user_info['domains'])

        # grab the user
        user = member.getUser()
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.portal_user_info['id'])
        self.assertEqual(user._getPassword(), self.portal_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), ('Authenticated',) + self.portal_user_info['roles']))
        self.assertEqual(user.getDomains(), self.portal_user_info['domains'])


    def testWrapUserRoot(self):
        portal = self.getPortal()
        newSecurityManager(None, self.root_user)
        member = portal.portal_membership.getAuthenticatedMember()

        # make sure all the member properties we set are correct
        self.failUnless(member != None)
        self.assertEqual(member.getId(), self.root_user_info['id'])
        self.assertEqual(member.getPassword(), self.root_user_info['password'])
        self.failUnless(self.compareTuples(member.getRoles(), self.root_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(member.getDomains(), self.root_user_info['domains'])

        # grab the user
        user = member.getUser()
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.root_user_info['id'])
        self.assertEqual(user._getPassword(), self.root_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), ('Authenticated',) + self.root_user_info['roles']))
        self.assertEqual(user.getDomains(), self.root_user_info['domains'])


    def testGetMemberById(self):
        portal = self.getPortal()
        member = self.membership.getMemberById(self.portal_user.getUserName())
        # make sure all the member properties we set are correct
        self.failUnless(member != None)
        self.assertEqual(member.getId(), self.portal_user_info['id'])
        self.assertEqual(member.getPassword(), self.portal_user_info['password'])
        self.failUnless(self.compareTuples(member.getRoles(), self.portal_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(member.getDomains(), self.portal_user_info['domains'])

        # grab the user
        user = member.getUser()
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.portal_user_info['id'])
        self.assertEqual(user._getPassword(), self.portal_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), ('Authenticated',) + self.portal_user_info['roles']))
        self.assertEqual(user.getDomains(), self.portal_user_info['domains'])


if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestUser))
        return suite
