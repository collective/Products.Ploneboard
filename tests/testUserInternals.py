import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFMember.tests import CMFMemberTestCase

from Products.CMFPlone.tests.PloneTestCase import default_user, portal_name

"""Make sure ownership and local roles are indexed properly"""

class TestUserInternals(CMFMemberTestCase.CMFMemberTestCase):

    def resultsContain(self, results, object):
        for r in results:
            if r.getObject() == object:
                return 1
        return 0


    def testUserInternals(self):
        portal = self.getPortal()
        # instantiate a member object so we can use a few private methods
        member = self.membership.getMemberById(self.portal_user.getUserName())

        test_user = self.portal_user
        info = member._getInfoFromUser(test_user)
        self.assertEqual(info, ('acl_users', test_user.getUserName()))
        user = member._getUserFromInfo(info)
        self.assertEqual(user.getUserName(), test_user.getUserName())
        self.assertEqual(aq_parent(user), aq_parent(aq_inner(test_user)))

        test_user = self.root_user
        info = member._getInfoFromUser(test_user)
        self.assertEqual(info, ('/acl_users', test_user.getUserName()))
        user = member._getUserFromInfo(info)
        self.assertEqual(user.getUserName(), test_user.getUserName())
        self.assertEqual(aq_parent(user), aq_parent(aq_inner(test_user)))


if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestUserInternals))
        return suite
