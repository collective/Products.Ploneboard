import unittest
import Zope     # product initialization
root = Zope.app()
from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember
import sys

class CMFMemberTest( SecurityRequestTest ):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        if hasattr(self.root, 'testsite'):
            self.root.manage_delObjects(['testsite'])
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( 'testsite' )
        self.testsite = getattr(self.root, 'testsite')
        sys.stdout.write(str(self.testsite.objectIds()))
        install_archetypes(self.testsite)
        install_cmfmember(self.testsite)

    def test_user(self):
        id = 'test_member'
        password = 'password'
        roles = ('Member',)
        domains = ('127.0.0.1',)

        # add a new member
        sys.stdout.write(str(self.testsite.acl_users.objectIds()))
        self.testsite.portal_membership.addMember(id, password, roles, domains)

        # get the member
        member = self.testsite.portal_membership.getMemberById(id)
        # make sure all the member properties we set are correct
        self.assertEqual(member.getMemberId(), id)
        self.assertEqual(member._getPassword(), password)
        self.assertEqual(member.getRoles(), roles+('Authenticated',))
        self.assertEqual(member.getDomains(), domains)

        # grab the user
        user = member.getUser()
        # make sure the user properties are correct
        self.assertEqual(user.getId(), id)
        self.assertEqual(user._getPassword(), password)
        self.assertEqual(user.getRoles(), roles+('Authenticated',))
        self.assertEqual(user.getDomains(), domains)

        password2 = 'password2'
        member._setPassword(password2)
        self.assertEqual(member._getPassword(), password2)
        member.setRoles('Member,Manager')
        self.assertEqual(member.getRoles(), ('Member','Manager','Authenticated'))
        member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(member.getDomains(), ('127.0.0.1','127.0.0.2'))

        sys.stdout.write(str(member.getUser().valid_roles)+'\n')
        sys.stdout.write(str(member.valid_roles)+'\n')
        sys.stdout.write(str(member.valid_roles()))

    def tearDown( self ):
        SecurityRequestTest.tearDown(self)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFMemberTest),
        ))

if __name__ == '__main__':
    unittest.main()