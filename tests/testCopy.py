import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFMember.tests import CMFMemberTestCase

class TestCopy(CMFMemberTestCase.CMFMemberTestCase):

    def testCopy(self):
        # Test renaming of a member whose corresponding user lives in the 
        # portal's acl_users
        
        self.createUserContent()
        portal = self.getPortal()

        # add a member corresponding to portal_user via wrapping m =
        portal.portal_membership.getMemberById(self.portal_user.getUserName())
#        get_transaction().commit(1)

        old_id = self.portal_user.getUserName()
        new_id = 'copy_of_' + old_id

        cb_copy_data = self.portal.portal_memberdata.manage_copyObjects([old_id])
        portal.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old user still exists
        user = self.getPortal().acl_users.getUser(old_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.portal_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.portal_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(user.getDomains(), self.portal_user_info['domains'])

        # make sure old member still exists
        member = self.getPortal().portal_membership.getMemberById(old_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), old_id)
        self.assertEqual(member.getPassword(), self.portal_user_info['password'])
        self.assertEqual(member.getRoles(), self.portal_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.portal_user_info['domains'])

        # make sure new member has been created
        member = self.getPortal().portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.portal_user_info['password'])
        self.assertEqual(member.getRoles(), self.portal_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.portal_user_info['domains'])

        # make sure new user has been created
        user = self.getPortal().acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.portal_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.portal_user_info['roles'] + ('Authenticated',)))

        # make sure appropriate ownership changes have been made
        user = self.getPortal().acl_users.getUser(new_id)

        folder1 = getattr(self.getPortal(), 'folder1', None)
        folder2 = getattr(self.getPortal(), 'folder2', None)
        
        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(self.root_user.getUserName())
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(old_id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))


    def xtestCopyRoot(self):
        # Test renaming of a member whose corresponding user lives in the 
        # zope root's acl_users
        
        self.createUserContent()
        portal = self.getPortal()

        # add a member corresponding to root_user via wrapping (since this is
        # how this would happen in real life
        newSecurityManager(None, self.root_user)
        m = portal.portal_membership.getAuthenticatedMember()
#        get_transaction().commit(1)
        
        old_id = m.getUserName()
        new_id = 'copy_of_' + old_id

        cb_copy_data = self.portal.portal_memberdata.manage_copyObjects([old_id])
        portal.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old user still exists
        user = self.app.acl_users.getUser(old_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.root_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(user.getDomains(), self.root_user_info['domains'])

        # make sure old member still exists
        member = self.getPortal().portal_membership.getMemberById(old_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), old_id)
        self.assertEqual(member.getPassword(), self.root_user_info['password'])
        self.assertEqual(member.getRoles(), self.root_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_user_info['domains'])

        # make sure new member has been created
        member = self.getPortal().portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.root_user_info['password'])
        self.assertEqual(member.getRoles(), self.root_user_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_user_info['domains'])

        # make sure new user has been created
        user = self.getPortal().acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_user_info['password'])
        self.failUnless(self.compareTuples(user.getRoles(), self.root_user_info['roles'] + ('Authenticated',)))
        self.assertEqual(user.getRoles(),  self.root_user_info['roles'] + ('Authenticated',) )
        self.assertEqual(user.getDomains(), self.root_user_info['domains'])

        # make sure appropriate ownership changes have been made
        user = self.getPortal().acl_users.getUser(new_id)

        folder1 = getattr(self.getPortal(), 'folder1', None)
        folder2 = getattr(self.getPortal(), 'folder2', None)
        
        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(old_id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder1.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(self.portal_user.getUserName())
        self.assertEqual(roles, ('Reviewer',))



if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestCopy))
        return suite
