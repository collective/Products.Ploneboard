import unittest
from BaseTest import BaseTest

class TestCopy(BaseTest):

    def test_copy(self):
        site = self._getSite()
        cb_copy_data = site.portal_memberdata.manage_copyObjects((self.member_info['id'],))
        site.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
        member = site.portal_membership.getMemberById(self.member_info['id'])
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.member_info['id'])
        self.assertEqual(member.getPassword(), self.member_info['password'])
#        self.assertEqual(member.getRoles(), self.member_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getRoles(), self.member_info['roles'])
        self.assertEqual(member.getDomains(), self.member_info['domains'])

        user = site.acl_users.getUser(self.member_info['id'])
        self.assertEqual(user, self._getUser())

        new_id = 'copy_of_' + self.member_info['id']
        # make sure member has been copied
#        member = site.portal_membership.getMemberById(new_id)
        member = site.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member.getPassword(), self.member_info['password'])
#        self.assertEqual(member.getRoles(), self.member_info['roles'] + ('Authenticated',))
        self.assertEqual(member.getRoles(), self.member_info['roles'])
        self.assertEqual(member.getDomains(), self.member_info['domains'])

        user = site.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.member_info['password'])
        self.assertEqual(user.getRoles(), self.member_info['roles'] + ('Authenticated',))
#        self.assertEqual(user.getRoles(), self.member_info['roles'])
        self.assertEqual(user.domains, self.member_info['domains'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestCopy),
        ))

if __name__ == '__main__':
    unittest.main()