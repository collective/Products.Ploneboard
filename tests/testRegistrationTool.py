import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase
from Products.CMFCore.utils import getToolByName
from Interface.Verify import verifyClass
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import Unauthorized
from AccessControl.SpecialUsers import nobody

import Products.CMFMember
from Products.CMFMember.MemberDataContainer import MemberDataContainer
from Products.CMFMember.Member import Member as MemberData

default_user = CMFMemberTestCase.default_user

_d = {'__ac_name': default_user,
      '__ac_password': 'secret'}

allowed_types = ('Member',)

class TestRegistrationTool(CMFMemberTestCase.CMFMemberTestCase):

    def afterSetUp(self):
        CMFMemberTestCase.CMFMemberTestCase.afterSetUp(self)
        self.setRoles([])
 
    
    def testMailPasswordApprovalUser(self):
        # http://plone.org/development/teams/developer/groups/issues/65
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(('Member',), 'member_approval_workflow')
        member = self.membership.getMemberById( self.portal_user_info['id'])
        member.setEmail('nobody@neverexistingdomain.fake')
        wf_tool.doActionFor( member, 'disable' )
        
        noSecurityManager()
        self.assertRaises(Unauthorized,
                          self.portal.portal_registration.mailPassword,
                          self.portal_user_info['id'], self.app.REQUEST)
            
        
if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestRegistrationTool))
        return suite

