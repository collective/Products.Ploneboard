import unittest
from BaseTest import BaseTest

class TestDeleteRoot(BaseTest):

    def test_deleteRoot(self):
        site = self._getSite()
        # a more complicated case -- the authenticated user lives in self.root.acl_users, not portal.acl_users

        site.portal_memberdata.manage_delObjects([self.root_member_info['id']])

        # make sure old member is gone
        member = site.portal_membership.getMemberById(self.root_member_info['id'])
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.root.acl_users.getUser(self.root_member_info['id'])
        self.failUnless(user != None)
        self.assertEqual(user, self._getRootUser())

        # make sure content not owned by the root user has not been deleted
        folder1 = getattr(site, 'folder1', None)
        self.failUnless(folder1 != None)

        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)

        # we do NOT delete content owned by the root user
        folder2 = getattr(site, 'folder2', None)
        self.failUnless(folder2 != None)

        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDeleteRoot),
        ))

if __name__ == '__main__':
    unittest.main()