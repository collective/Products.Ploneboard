import unittest
from BaseTest import BaseTest

class TestUser(BaseTest):

    def test_user(self):
        member = self._getMember()
        # make sure all the member properties we set are correct
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.member_info['id'])
        self.assertEqual(member.getPassword(), self.member_info['password'])
        self.assertEqual(member.getRoles(), self.member_info['roles'])
        self.assertEqual(member.getDomains(), self.member_info['domains'])

        # grab the user
        user = member.getUser()
        self.assertEqual(user, self._getUser())
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.member_info['id'])
        self.assertEqual(user._getPassword(), self.member_info['password'])
        self.assertEqual(user.getRoles(), self.member_info['roles'] + ('Authenticated',))
        self.assertEqual(user.getDomains(), self.member_info['domains'])

        password2 = 'password2'
        member._setPassword(password2)
        self.assertEqual(member.getPassword(), password2)
        member.setRoles('Member, Manager')
        self.assertEqual(member.getRoles(), ('Member', 'Manager'))
        member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(member.getDomains(), ('127.0.0.1', '127.0.0.2'))

    def test_root_user(self):
        member = self._getRootMember()
        # make sure all the member properties we set are correct
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.root_member_info['id'])
        self.assertEqual(member.getPassword(), self.root_member_info['password'])
        self.assertEqual(member.getRoles(), self.root_member_info['roles'])
        self.assertEqual(member.getDomains(), self.root_member_info['domains'])

        # grab the user
        user = member.getUser()
        self.assertEqual(user, self._getRootUser())
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.root_member_info['id'])
        self.assertEqual(user._getPassword(), self.root_member_info['password'])
        self.assertEqual(user.getRoles(), self.root_member_info['roles'] + ('Authenticated',))
        self.assertEqual(user.getDomains(), self.root_member_info['domains'])

        password2 = 'password2'
        member._setPassword(password2)
        self.assertEqual(member.getPassword(), password2)
        member.setRoles('Member, Manager')
#       XXX - the current getRoles method filters out roles not available to
#       the member's user's acl_users folder.  I'm not sure if that's the best
#       approach -- maybe we should allow any portal roles?  OTOH, that creates
#       the problem of having different portals all assigning different roles
#       to the same user.
#        self.assertEqual(member.getRoles(), ('Member', 'Manager'))
        self.assertEqual(member.getRoles(), ('Manager',))
        member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(member.getDomains(), ('127.0.0.1', '127.0.0.2'))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUser),
        ))

if __name__ == '__main__':
    unittest.main()