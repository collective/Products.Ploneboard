import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase
from Products.CMFCore.utils import getToolByName
from Interface.Verify import verifyClass
from AccessControl.SecurityManagement import newSecurityManager

import Products.CMFMember
from Products.CMFMember.Member import Member

class TestMember(CMFMemberTestCase.CMFMemberTestCase):

    def testMemberDataInterface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import MemberData as IMemberData
        verifyClass(IMemberData, Member)

    def testMemberTitle(self):
        # title should failover to member id
        p_u_info = self.portal_user_info
        portal_member = self.membership.getMemberById(p_u_info['id'])
        self.failUnless(portal_member.Title() == p_u_info['id'])

        test_title = 'TEST_TITLE'
        portal_member.setTitle(test_title)
        self.failUnless(portal_member.Title() == test_title)

        portal_member.setTitle('')
        self.failUnless(portal_member.Title() == p_u_info['id'])        

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMember))
        return suite
