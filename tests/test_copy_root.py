import unittest
from BaseTest import BaseTest

class TestCopyRoot(BaseTest):

    def test_copyRoot(self):
        site = self._getSite()
        cb_copy_data = site.portal_memberdata.manage_copyObjects((self.root_member_info['id'],))
        site.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
#        member = site.portal_membership.getMemberById(self.root_member_info['id'])
        member = site.portal_memberdata.get(self.root_member_info['id'], None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.root_member_info['id'])
        self.assertEqual(member.getPassword(), self.root_member_info['password'])
        self.assertEqual(member.getRoles(), self.root_member_info['roles'])
        self.assertEqual(member.getDomains(), self.root_member_info['domains'])

        user = self.root.acl_users.getUser(self.root_member_info['id'])
        self.assertEqual(user, self._getRootUser())

        new_id = 'copy_of_' + self.root_member_info['id']
        # make sure member has been copied
#        member = site.portal_membership.getMemberById(new_id)
        member = site.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.root_member_info['password'])
        self.assertEqual(member.getRoles(), self.root_member_info['roles'])
        self.assertEqual(member.getDomains(), self.root_member_info['domains'])

        user = site.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_member_info['password'])
        self.assertEqual(user.getRoles(), self.root_member_info['roles'] + ('Authenticated',))
        self.assertEqual(user.domains, self.root_member_info['domains'])

        user = self.root.acl_users.getUser(new_id)
        self.assertEqual(user, None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestCopyRoot),
        ))

if __name__ == '__main__':
    unittest.main()