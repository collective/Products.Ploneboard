import unittest
from BaseTest import BaseTest

class TestRenameRoot(BaseTest):

    # a more complicated case -- the authenticated user lives in self.root.acl_users, not portal.acl_users
    def test_renameRoot(self):
        site = self._getSite()
        new_id = 'id2'
        site.portal_memberdata.manage_renameObjects((self.root_member_info['id'],),(new_id,))

        # make sure member has been moved
        member = site.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.root_member_info['password'])
#        self.assertEqual(member.getRoles(), self.root_member_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getRoles(), self.root_member_info['roles'])
        self.assertEqual(member.getDomains(), self.root_member_info['domains'])

        # make sure old member is gone
        member = site.portal_membership.getMemberById(self.root_member_info['id'])
        self.assertEqual(member, None)

        # make sure member has been copied
        user = site.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_member_info['password'])
        self.assertEqual(user.getRoles(), self.root_member_info['roles'] + ('Authenticated',))
#        self.assertEqual(user.getRoles(), self.root_member_info['roles'])
        self.assertEqual(user.domains, self.root_member_info['domains'])

        # make sure old user is still there gone
        user = self.root.acl_users.getUser(self.root_member_info['id'])
        self.failUnless(user != None)
        self.assertEqual(user, self._getRootUser())


        # make sure appropriate ownership changes have been made
        user = site.acl_users.getUser(new_id)

        folder1 = getattr(site, 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.failUnless(owner == self._getUser())
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.failUnless(owner == self._getUser())

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.failUnless(owner == user)

        folder2 = getattr(site, 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.failUnless(owner == user)

        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.failUnless(owner == self._getUser())

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.failUnless(owner == user)

        # make sure local roles get updated
        roles = folder2.get_local_roles_for_userid(self.member_info['id'])
        self.assertEqual(roles, ('Reviewer',))

        roles = folder1.get_local_roles_for_userid(self.root_member_info['id'])
        self.assertEqual(roles, ())

        roles = folder1.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestRenameRoot),
        ))

if __name__ == '__main__':
    unittest.main()