import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFMember.tests import CMFMemberTestCase

""" test renaming a member """

class TestRename(CMFMemberTestCase.CMFMemberTestCase):
    
    def testRename(self):
        # Test renaming of a member whose corresponding user lives in the 
        # portal's acl_users

        self.createUserContent()
        portal = self.getPortal()

        # add a member corresponding to portal_user via wrapping
        m = portal.portal_membership.getMemberById(self.portal_user.getUserName())
        get_transaction().commit(1)

        old_id = self.portal_user.getUserName()
        new_id = 'id2'
        portal.portal_memberdata.manage_renameObjects((m.getId(),),(new_id,))

        # make sure member has been moved
        member = self.getPortal().portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.portal_user_info['password'])
        self.assertEqual(member.getRoles(), self.portal_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.portal_user_info['domains'])

        # make sure old member is gone
        member = self.getPortal().portal_membership.getMemberById(old_id)
        self.assertEqual(member, None)

        # make sure corresponding user has been moved
        user = self.getPortal().acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.portal_user_info['password'])
        self.assertEqual(user.getRoles(),  self.portal_user_info['roles'] + ('Authenticated',))
        self.assertEqual(user.getDomains(), self.portal_user_info['domains'])

        # make sure old user is gone
        user = self.getPortal().acl_users.getUser(old_id)
        self.assertEqual(user, None)

        # make sure appropriate ownership changes have been made
        user = self.getPortal().acl_users.getUser(new_id)

        folder1 = getattr(self.getPortal(), 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.assertEqual(owner.getUserName(), self.root_user.getUserName())

        folder2 = getattr(self.getPortal(), 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.assertEqual(owner.getUserName(), self.root_user.getUserName())
        
        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())
        
        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.assertEqual(owner.getUserName(), self.root_user.getUserName())
        
        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(self.root_user.getUserName())
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(old_id)
        self.assertEqual(roles, ())

        roles = folder2.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))



    def testRenameRoot(self):
        # Test renaming of a member whose corresponding user lives in the Zope 
        # root's acl_users
        
        self.createUserContent()
        portal = self.getPortal()
        old_id = self.root_user.getUserName()

        # add a member corresponding to root_user via wrapping (since this is
        # how this would happen in real life
        newSecurityManager(None, self.root_user)
        m = portal.portal_membership.getAuthenticatedMember()

        get_transaction().commit(1)

        new_id = 'id3'
        portal.portal_memberdata.manage_renameObjects((old_id,),(new_id,))


        # make sure old member is gone
        member = portal.portal_membership.getMemberById(old_id)
        self.assertEqual(member, None)

        # make sure member has been moved
#        member = self.getPortal().portal_membership.getMemberById(new_id)
        member = portal.portal_memberdata.get(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.root_user_info['password'])
        self.assertEqual(member.getRoles(), self.root_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_user_info['domains'])

        # make sure corresponding user has NOT been moved
        user = self.app.acl_users.getUser(old_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.root_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(user.getDomains(), self.root_user_info['domains'])

        # make sure new user has been created
        user = self.getPortal().acl_users.getUser(new_id)
        self.assertNotEqual(user, None)
        self.assertEqual(user.__, self.root_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.root_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(user.getDomains(), self.root_user_info['domains'])


        # make sure appropriate ownership changes have been made

        folder1 = getattr(self.getPortal(), 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.assertEqual(owner.getUserName(), self.portal_user.getUserName())
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.assertEqual(owner.getUserName(), self.portal_user.getUserName())

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())

        folder2 = getattr(self.getPortal(), 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())
        
        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.assertEqual(owner.getUserName(), self.portal_user.getUserName())
        
        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.assertEqual(owner.getUserName(), user.getUserName())
        
        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(old_id)
        self.assertEqual(roles, ())

        roles = folder1.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(old_id)
        self.assertEqual(roles, ())

        roles = folder2.get_local_roles_for_userid(self.portal_user_info['id'])
        self.assertEqual(roles, ('Reviewer',))

                         
if __name__ == '__main__':
        framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestRename))
        return suite
