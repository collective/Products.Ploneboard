import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase
from Interface.Verify import verifyClass
from AccessControl import getSecurityManager

import Products.CMFMember
from Products.CMFMember.MemberDataContainer import MemberDataContainer
from Products.CMFMember.Member import Member as MemberData

class TestLoginInfoSchema(CMFMemberTestCase.CMFMemberTestCase):

    def testLastLoginTime(self):

        member = self.portal.portal_membership.getAuthenticatedMember()
        member_id = member.id

        # grab the last login time (should be 2000/01/01)
        first_login_time = member.getLastLoginTime()

        # logout
        self.logout()
        
        # login     
        self.login(member_id)
        self.portal.login_success()

        # log them out again
        self.logout()
        
        # log back in and compare        
        self.login(member_id)
        self.portal.login_success()
        
        new_login_time = member.getLastLoginTime()
        
        self.assertNotEqual( first_login_time, new_login_time, "%s was not set [ %s ]" % (first_login_time, new_login_time ))

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestLoginInfoSchema))
        return suite

