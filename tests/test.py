import unittest
import Zope     # product initialization
root = Zope.app()
from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember

from AccessControl.SecurityManagement import newSecurityManager

import sys

site = 'testsite'

class CMFMemberTest( SecurityRequestTest ):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        if hasattr(self.root, site):
            self.root.manage_delObjects([site])
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( site )

        self.root.acl_users.userFolderAddUser('admin', 'foo', ('Manager','Member',), ())

        self.testsite = getattr(self.root, site)
        install_archetypes(self.testsite)
        install_cmfmember(self.testsite)

        self.id = 'test_member'
        self.password = 'password'
        self.roles = ('Member',)
        self.domains = ('127.0.0.1',)

        # add a new member
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))

        self.testsite.portal_membership.addMember(self.id, self.password, self.roles, self.domains)
        self.user = self.testsite.acl_users.getUser(self.id)
        # force creation of user via wrapUser
        self.member = self.testsite.portal_membership.getMemberById(self.id)

        self.root_id = 'root_member'
        self.root_password = 'root_password'
        self.root_roles = ('Manager','Reviewer','Member',)
        self.root_domains = ('127.0.0.1',)

        self.root.acl_users.userFolderAddUser(self.root_id, self.root_password, self.root_roles, self.root_domains)
        self.root_user = self.root.acl_users.getUser(self.root_id)

        newSecurityManager(None, self.root_user.__of__(self.root.acl_users))
        # force creation of user via wrapUser
        self.root_member = self.testsite.portal_membership.getAuthenticatedMember()
#        self.root_member = self.testsite.portal_memberdata.get(self.root_id, None)
        
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))
        get_transaction().commit()


    def tearDown( self ):
        if hasattr(self.root, 'testsite'):
            self.root.manage_delObjects(['testsite'])
        self.testsite = None
        SecurityRequestTest.tearDown(self)


    def test_user(self):
        # make sure all the member properties we set are correct
        self.failUnless(self.member != None)
        self.assertEqual(self.member.getMemberId(), self.id)
        self.assertEqual(self.member._getPassword(), self.password)
        self.assertEqual(self.member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(self.member.getDomains(), self.domains)

        # grab the user
        user = self.member.getUser()
        self.assertEqual(user, self.user)
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.id)
        self.assertEqual(user._getPassword(), self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.getDomains(), self.domains)

        password2 = 'password2'
        self.member._setPassword(password2)
        self.assertEqual(self.member._getPassword(), password2)
        self.member.setRoles('Member,Manager')
        self.assertEqual(self.member.getRoles(), ('Member','Manager','Authenticated'))
        self.member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(self.member.getDomains(), ('127.0.0.1','127.0.0.2'))


    def test_delete(self):
        self.testsite.portal_memberdata.manage_delObjects([self.id])

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, None)


    def test_deleteRoot(self):
        # a more complicated case -- the authenticated user lives in root.acl_users, not portal.acl_users

        self.testsite.portal_memberdata.manage_delObjects([self.root_id])

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.root_id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.root.acl_users.getUser(self.root_id)
        self.failUnless(user != None)
        self.assertEqual(user, self.root_user)


    def test_rename(self):
        new_id = 'id2'
        self.testsite.portal_memberdata.manage_renameObjects((self.id,),(new_id,))

        # make sure member has been moved
        member = self.testsite.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.domains, self.domains)

        # make sure old user is gone
        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, None)


    # a more complicated case -- the authenticated user lives in root.acl_users, not portal.acl_users
    def test_renameRoot(self):
        new_id = 'id2'
        self.testsite.portal_memberdata.manage_renameObjects((self.root_id,),(new_id,))

        # make sure member has been moved
        member = self.testsite.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.root_id)
        self.assertEqual(member, None)

        # make sure member has been copied
        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_password)
        self.assertEqual(user.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(user.domains, self.root_domains)

        # make sure old user is still there gone
        user = self.root.acl_users.getUser(self.root_id)
        self.failUnless(user != None)
        self.assertEqual(user, self.root_user)


    def test_copy(self):
        cb_copy_data = self.testsite.portal_memberdata.manage_copyObjects((self.id,))
        self.testsite.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, self.user)

        new_id = 'copy_of_' + self.id
        # make sure member has been copied
#        member = self.testsite.portal_membership.getMemberById(new_id)
        member = self.testsite.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.domains, self.domains)


    def test_copy_root(self):
        cb_copy_data = self.testsite.portal_memberdata.manage_copyObjects((self.root_id,))
        self.testsite.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
#        member = self.testsite.portal_membership.getMemberById(self.root_id)
        member = self.testsite.portal_memberdata.get(self.root_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.root_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        user = self.root.acl_users.getUser(self.root_id)
        self.assertEqual(user, self.root_user)

        new_id = 'copy_of_' + self.root_id
        # make sure member has been copied
#        member = self.testsite.portal_membership.getMemberById(new_id)
        member = self.testsite.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_password)
        self.assertEqual(user.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(user.domains, self.root_domains)

        user = self.root.acl_users.getUser(new_id)
        self.assertEqual(user, None)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFMemberTest),
        ))

if __name__ == '__main__':
    unittest.main()