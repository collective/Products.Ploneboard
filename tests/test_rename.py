import unittest
from BaseTest import BaseTest

class TestRename(BaseTest):

    def test_rename(self):
        site = self._getSite()
        new_id = 'id2'
        site.portal_memberdata.manage_renameObjects((self.member_info['id'],),(new_id,))

        # make sure member has been moved
        member = site.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.member_info['password'])
#        self.assertEqual(member.getRoles(), self.member_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getRoles(), self.member_info['roles'])
        self.assertEqual(member.getDomains(), self.member_info['domains'])

        # make sure old member is gone
        member = site.portal_membership.getMemberById(self.member_info['id'])
        self.assertEqual(member, None)

        # make sure member has been moved
        user = site.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.member_info['password'])
        self.assertEqual(user.getRoles(), self.member_info['roles'] + ('Authenticated',))
#        self.assertEqual(user.getRoles(), self.member_info['roles'])
        self.assertEqual(user.domains, self.member_info['domains'])

        # make sure old user is gone
        user = site.acl_users.getUser(self.member_info['id'])
        self.assertEqual(user, None)

        # make sure appropriate ownership changes have been made
        user = site.acl_users.getUser(new_id)

        folder1 = getattr(site, 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.failUnless(owner == user)
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.failUnless(owner == user)

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.failUnless(owner == self._getRootUser())

        folder2 = getattr(site, 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.failUnless(owner == self._getRootUser())

        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.failUnless(owner == user)

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.failUnless(owner == self._getRootUser())

        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(self.root_member_info['id'])
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(self.member_info['id'])
        self.assertEqual(roles, ())

        roles = folder2.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestRename),
        ))

if __name__ == '__main__':
    unittest.main()