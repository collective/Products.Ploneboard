import unittest
from BaseTest import BaseTest

class TestDelete(BaseTest):

    def test_delete(self):
        site = self._getSite()
        site.portal_memberdata.manage_delObjects([self.member_info['id']])

        # make sure old member is gone
        member = site.portal_membership.getMemberById(self.member_info['id'])
        self.assertEqual(member, None)

        # make sure member has been moved
        user = site.acl_users.getUser(self.member_info['id'])
        self.assertEqual(user, None)

        # make sure appropriate content has been deleted
        folder1 = getattr(site, 'folder1', None)
        self.assertEqual(folder1, None)

        folder2 = getattr(site, 'folder2', None)
        self.failUnless(folder2 != None)

        doc3 = getattr(folder2, 'doc3', None)
        self.assertEqual(doc3, None)

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)

        # make sure local roles get deleted
        roles = folder2.get_local_roles_for_userid(self.member_info['id'])
        self.assertEqual(roles, ())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDelete),
        ))

if __name__ == '__main__':
    unittest.main()