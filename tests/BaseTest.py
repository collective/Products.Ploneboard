import unittest
import Zope     # product initialization
Zope.startup()
from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember

from AccessControl.SecurityManagement import newSecurityManager

import sys

class BaseTest(SecurityRequestTest):

    site_id = 'unittest_testsite'
    member_info = {'id':'unittest_test_member', 'password':'password', 'roles':('Member','Reviewer',), 'domains':('127.0.0.1',)}
    root_member_info = {'id':'unittest_root_member', 'password':'password2', 'roles':('Manager',), 'domains':('127.0.0.2',)}
    admin_info = {'id':'unittest_admin', 'password':'password', 'roles':('Manager','Member',), 'domains':()}
    
    
    def setUp( self ):
        SecurityRequestTest.setUp(self)
        # create an admin user
        self.root.acl_users.userFolderAddUser(self.admin_info['id'], 
                                              self.admin_info['password'], 
                                              self.admin_info['roles'], 
                                              self.admin_info['domains'])
        get_transaction().commit()
        test_admin = self.root.acl_users.getUser(self.admin_info['id']).__of__(self.root.acl_users)
        # assume role of test_admin
        newSecurityManager(None, test_admin)

        if hasattr(self.root, self.site_id):
            self.root.manage_delObjects([self.site_id])
            get_transaction().commit()
        self.root.manage_addProduct['CMFPlone'].manage_addSite(self.site_id)
        get_transaction().commit()

        site = getattr(self.root, self.site_id)

        install_archetypes(site)
        install_cmfmember(site)

        site.acl_users.userFolderAddUser(self.member_info['id'], 
                                         self.member_info['password'], 
                                         self.member_info['roles'], 
                                         self.member_info['domains'])
        user = site.acl_users.getUser(self.member_info['id']).__of__(site.acl_users)
        assert(user != None)
        member = site.portal_membership.getMemberById(self.member_info['id'])

        self.root.acl_users.userFolderAddUser(self.root_member_info['id'],
                                              self.root_member_info['password'], 
                                              self.root_member_info['roles'], 
                                              self.root_member_info['domains'])
        root_user = self.root.acl_users.getUser(self.root_member_info['id']).__of__(self.root.acl_users)

#        # force creation of user via wrapUser
        newSecurityManager(None, root_user)
        root_member = site.portal_membership.getAuthenticatedMember()
        
        newSecurityManager(None, test_admin)

        # create some content
        site.invokeFactory(id='folder1', type_name='Folder')
        folder1 = getattr(site, 'folder1')
        folder1.changeOwnership(user)
        folder1.manage_addLocalRoles(self.root_member_info['id'], ('Reviewer',))
        
        folder1.invokeFactory(id='doc1', type_name='Document')
        doc1 = getattr(folder1, 'doc1')
        doc1.changeOwnership(user)

        folder1.invokeFactory(id='doc2', type_name='Document')
        doc2 = getattr(folder1, 'doc2')
        doc2.changeOwnership(root_user)

        site.invokeFactory(id='folder2', type_name='Folder')
        folder2 = getattr(site, 'folder2')
        folder2.changeOwnership(root_user)
        folder2.manage_addLocalRoles(self.member_info['id'], ('Reviewer',))

        folder2.invokeFactory(id='doc3', type_name='Document')
        doc3 = getattr(folder2, 'doc3')
        doc3.changeOwnership(user)

        folder2.invokeFactory(id='doc4', type_name='Document')
        doc4 = getattr(folder2, 'doc4')
        doc4.changeOwnership(root_user)
        
        get_transaction().commit()

        self.assertEqual(doc2.getOwner(0), self._getRootUser())
        folder1.changeOwnership(user)
        doc2 = getattr(folder1, 'doc2')
        self.assertEqual(doc2.getOwner(0), self._getRootUser())


    def tearDown( self ):
        # get rid of the test site we added
        if hasattr(self.root, self.site_id):
            self.root.manage_delObjects([self.site_id])
            get_transaction().commit()
        # get rid of the users we added
        if self.root.acl_users.getUser(self.admin_info['id']):
            self.root.acl_users.userFolderDelUsers([self.admin_info['id']])
        if self.root.acl_users.getUser(self.root_member_info['id']):
            self.root.acl_users.userFolderDelUsers([self.root_member_info['id']])

        # pack the zodb so that it doesn't get huge
        get_transaction().commit()
        self.root.Control_Panel.Database.manage_pack()
        get_transaction().commit()

        SecurityRequestTest.tearDown(self)


    def _getSite(self):
        return getattr(self.root, self.site_id)


    def _getUser(self):
        return self._getSite().acl_users.getUser(self.member_info['id'])


    def _getRootUser(self):
        return self.root.acl_users.getUser(self.root_member_info['id'])


    def _getMember(self):
        return self._getSite().portal_membership.getMemberById(self.member_info['id'])

    
    def _getRootMember(self):
        return self._getSite().portal_memberdata.get(self.root_member_info['id'])
#        return self._getSite().portal_membership.getMemberById(self.root_member_info['id'])