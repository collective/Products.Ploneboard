import unittest
import Zope     # product initialization
root = Zope.app()
from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember
from Products.CMFMemberTest.Extensions.Install import install as install_cmfmembertest

from AccessControl.SecurityManagement import newSecurityManager

import sys

site = 'testsite'

class CMFMemberMigrationTest( SecurityRequestTest ):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        # create an admin user
        self.root.acl_users.userFolderAddUser('admin', 'qwerty', ('Manager','Member',), ())
        get_transaction().commit()
        # assume role of admin
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))

        if hasattr(self.root, site):
            self.root.manage_delObjects([site])
            get_transaction().commit()
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( site )
        get_transaction().commit()

        self.testsite = getattr(self.root, site)

        install_archetypes(self.testsite)

        membership_tool = self.testsite.portal_membership

        self.a = {'id':'a', 'password':'123', 'roles':('Member',), 'domains':('127.0.0.1',), 'email':'A'}
        membership_tool.addMember(self.a['id'], self.a['password'], self.a['roles'], self.a['domains'])
        a = membership_tool.getMemberById('a')
        a.setMemberProperties({'email':self.a['email']})

        self.b = {'id':'b', 'password':'456', 'roles':('Member','Reviewer'), 'domains':(), 'email':'B'}
        membership_tool.addMember(self.b['id'], self.b['password'], self.b['roles'], self.b['domains'])
        b = membership_tool.getMemberById('b')
        b.setMemberProperties({'email':self.b['email']})

        # force creation of an admin member via wrapUser
#        root_member = self.testsite.portal_membership.getAuthenticatedMember()
#        admin = membership_tool.getMemberById('admin')


    def tearDown( self ):
        self.testsite = None

        if hasattr(self.root, site):
            self.root.manage_delObjects([site])
            get_transaction().commit()
        SecurityRequestTest.tearDown(self)


    def testMigration1(self):
        install_cmfmember(self.testsite)
        self._compare_members()
        get_transaction().commit()

        install_cmfmembertest(self.testsite)
        self._compare_members()
        get_transaction().commit()


    def _compare_members(self):
        membership_tool = self.testsite.portal_membership

        a = membership_tool.getMemberById('a')
        self.assertEqual(a.getMemberId(), self.a['id'])
        self.assertEqual(a._getPassword(), self.a['password'])
        self.assertEqual(a.getRoles(), self.a['roles']+('Authenticated',))
        self.assertEqual(a.getDomains(), self.a['domains'])
        self.assertEqual(a.email, self.a['email'])
        
        b = membership_tool.getMemberById('b')
        self.assertEqual(b.getMemberId(), self.b['id'])
        self.assertEqual(b._getPassword(), self.b['password'])
        self.assertEqual(b.getRoles(), self.b['roles']+('Authenticated',))
        self.assertEqual(b.getDomains(), self.b['domains'])
        self.assertEqual(b.email, self.b['email'])

#        admin = membership_tool.getMemberById('admin')
#        self.assertEqual(admin.getMemberId(), 'admin')
#        self.assertEqual(admin._getPassword(), 'qwerty')
#        self.assertEqual(admin.getRoles(), ('Manager','Member','Authenticated',))
#        self.assertEqual(admin.getDomains(), ())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFMemberTest),
        ))

if __name__ == '__main__':
    unittest.main()