import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], '../framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFMember.tests.oldMember import CMFMemberTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName, ToolInit
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember


class TestOld2NewMigration( CMFMemberTestCase.CMFMemberTestCase ):

    def afterSetUp( self ):
        # assume role of test_admin
        newSecurityManager(None, self.portal.acl_users.getUser(self.admin_user_info['id']).__of__(self.portal.acl_users))

        # add users to old MemberDataTool
        self.site = self.getPortal()
        membership_tool = self.portal.portal_membership
        self.a = {'id':'a', 'password':'123', 'roles':('Member',), 'domains':('127.0.0.1',), 'email':'A@dummy'}
        membership_tool.addMember(self.a['id'], self.a['password'], self.a['roles'], self.a['domains'])
        a = membership_tool.getMemberById('a')
        a.setMemberProperties({'email':self.a['email']})

        self.b = {'id':'b', 'password':'456', 'roles':('Member','Reviewer'), 'domains':(), 'email':'B@dummy'}
        membership_tool.addMember(self.b['id'], self.b['password'], self.b['roles'], self.b['domains'])
        b = membership_tool.getMemberById('b')
        b.setMemberProperties({'email':self.b['email']})

        # install new CMFMember
        qi = self.portal.portal_quickinstaller
        qi.installProduct('CMFMember')


    def installExampleMember(self):
        pass

    def testMigrationOldCMFMember2CMFMember(self):
        self.portal.cmfmember_control.upgrade()
        self.assertEqual(self.portal.portal_memberdata.__class__.portal_type, 'MemberDataContainer')


    def _compare_members(self):
        membership_tool = self.site.portal_membership

        a = membership_tool.getMemberById('a')
        self.assertEqual(a.getMemberId(), self.a['id'])
        self.assertEqual(a.getPassword(), self.a['password'])
        self.assertEqual(a.getRoles(), self.a['roles'])
        self.assertEqual(a.getDomains(), self.a['domains'])
        self.assertEqual(a.email, self.a['email'])
        
        b = membership_tool.getMemberById('b')
        self.assertEqual(b.getMemberId(), self.b['id'])
        self.assertEqual(b.getPassword(), self.b['password'])
        self.assertEqual(b.getRoles(), self.b['roles'])
        self.assertEqual(b.getDomains(), self.b['domains'])
        self.assertEqual(b.email, self.b['email'])

#        test_admin = membership_tool.getMemberById('test_admin')
#        self.assertEqual(test_admin.getMemberId(), 'test_admin')
#        self.assertEqual(test_admin.getPassword(), 'qwerty')
#        self.assertEqual(test_admin.getRoles(), ('Manager','Member','Authenticated',))
#        self.assertEqual(test_admin.getDomains(), ())

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestOld2NewMigration))
        return suite
