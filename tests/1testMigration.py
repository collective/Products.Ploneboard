import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('CMFMember')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')

from Products.CMFPlone.tests import PloneTestCase as PloneTestCase
import Products.CMFPlone as CMFPlone
import Products.CMFCore as CMFCore
from Products.CMFMember.Extensions.Install import install as install_cmfmember
from Products.CMFMemberExample.Extensions.Install import install as install_cmfmemberexample
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName, ToolInit

usera = {'id':'a','password':'123', 'roles':('Member',), 'domains':('127.0.0.1',), 'email':'A', 'fullname':'A Fuler'}
userb = {'id':'b', 'password':'456', 'roles':('Member','Reviewer',), 'domains':(), 'email':'B', 'fullname':'B Fuler'}

class TestMigration( PloneTestCase.PloneTestCase ):

    def beforeSetUp(self):
        pass
    
    def afterSetUp( self ):
        from Products.CMFMember.Extensions.Install import install as install_cmfmember
        install_cmfmember(self.portal)
        # create an admin user
        self.portal.acl_users.userFolderAddUser('test_admin', 'qwerty', ('Manager','Member',), ())
        get_transaction().commit(1)
        # assume role of test_admin
        newSecurityManager(None, self.portal.acl_users.getUser('test_admin').__of__(self.portal.acl_users))


        membership_tool = self.portal.portal_membership

        membership_tool.addMember(usera['id'], usera['password'], usera['roles'], usera['domains'])
        a = membership_tool.getMemberById(usera['id'])
        a.setMemberProperties({'email':usera['email'],
                               'fullname':usera['fullname']})

        membership_tool.addMember(userb['id'], userb['password'], userb['roles'], userb['domains'])
        b = membership_tool.getMemberById(userb['id'])
        b.setMemberProperties({'email':userb['email'],
                               'fullname':userb['fullname']})
        
    def testMigrationPlone2CMFMember(self):
        # check that we have what we should have before migration
        self.assertEquals(self.portal.portal_memberdata.__class__, CMFPlone.MemberDataTool.MemberDataTool)
        self._compare_members()

        # migrate Plone member stuff to CMFMember
        self.portal.cmfmember_control.upgrade()

        # check that we still have everything we had before
        self.assertEquals(self.portal.portal_memberdata.__class__.portal_type, 'MemberDataContainer')
        self._compare_members()
        
        self.assertEquals(self.portal.portal_memberdata.a.portal_type, 'Member')
        self.assertEquals(self.portal.portal_memberdata.b.portal_type, 'Member')
        
    def _compare_members(self):
        membership_tool = self.portal.portal_membership

        a = membership_tool.getMemberById(usera['id'])
        self.assertEqual(a.getMemberId(), usera['id'])
        self.assertEqual(a.getPassword(), usera['password'])
        self.assertEqual(a.getUser().getRoles(), usera['roles'] + ('Authenticated',))
        self.assertEqual(a.getDomains(), usera['domains'])
        self.assertEqual(a.getProperty('email'), usera['email'])
        self.assertEqual(a.getProperty('fullname'), usera['fullname'])
        
        b = membership_tool.getMemberById(userb['id'])
        self.assertEqual(b.getMemberId(), userb['id'])
        self.assertEqual(b.getPassword(), userb['password'])
        self.assertEqual(b.getUser().getRoles(), userb['roles'] + ('Authenticated',))
        self.assertEqual(b.getDomains(), userb['domains'])
        self.assertEqual(b.getProperty('email'), userb['email'])
        self.assertEqual(b.getProperty('fullname'), userb['fullname'])        

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMigration))
        return suite
