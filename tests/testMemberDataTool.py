import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase
from Products.CMFCore.utils import getToolByName
from Interface.Verify import verifyClass

import Products.CMFMember
from Products.CMFMember.MemberDataContainer import MemberDataContainer
from Products.CMFMember.Member import Member as MemberData

default_user = CMFMemberTestCase.default_user
_d = {'__ac_name': default_user,
      '__ac_password': 'secret'}

allowed_types = ('Member', 'ZCatalog')

class TestMemberDataContainer(ZopeTestCase.Functional, CMFMemberTestCase.CMFMemberTestCase):

    def afterSetUp(self):
        CMFMemberTestCase.CMFMemberTestCase.afterSetUp(self)
 
    def testAddNewMemberAndPruneOrphans(self):
        self.membership.addMember('orphanSoon', 'secret',['Member'],[])
        noMembers = self.memberdata.getMemberDataContents()[0]
        noMember = noMembers['member_count']
        noOrphans = noMembers['orphan_count']
        self.assertEqual(noOrphans, 0)
        self.memberdata.pruneMemberDataContents()
        noMembers = self.memberdata.getMemberDataContents()[0]
        self.assertEqual(noMembers['orphan_count'], 0)

    def testDeleteUserInAclUsersAndPruneOrphans(self):

        #set an email to have a Member object created
        
        tmpUser = self.membership.getMemberById(self.portal_user_info['id'])
        self.failUnless(tmpUser)
        tmpUser.setMemberProperties({'email': 'foo@bar.com'})

        #check that we don't have any orphans before we begin

        noMembers = self.memberdata.getMemberDataContents()[0]
        self.failIf(noMembers['member_count'] == 0)
        self.assertEqual(noMembers['orphan_count'], 0)

        #delete the user in acl_users and check if we have one orphan

        self.portal.acl_users.userFolderDelUsers((self.portal_user_info['id'],))
        noMembers = self.memberdata.getMemberDataContents()[0]
        self.assertEqual(noMembers['orphan_count'], 1)

        #remove orphans and check that no are left

        self.memberdata.pruneMemberDataContents()
        noMembers = self.memberdata.getMemberDataContents()[0]
        self.assertEqual(noMembers['orphan_count'], 0)

    def testAllowedMemberTypesInstanceDefault(self):
        for memberType in self.memberdata.allowedContentTypes():
            self.failIf(not memberType.getId() in self.memberdata.allowed_content_types)

    def testAllowedMemberTypesInstanceChanged(self):

        # check that everything is ok before we change
        self.assertEqual(list(self.memberdata.getAllowedMemberTypes()),
                        ['Member'])
        memberdataType = getToolByName(self.portal, 'portal_types').MemberDataContainer
        self.assertEqual(memberdataType.allowed_content_types, allowed_types)

        # change and compare to the type and local instance
        self.memberdata.setAllowedMemberTypes(('Member1','Member2',))

        # check member types for instance 
        self.assertEqual(list(self.memberdata.getAllowedMemberTypes()),
                        ['Member1','Member2'])

        # check member types for memberdata type 
        self.assertEqual(memberdataType.allowed_content_types, allowed_types)

class TestMemberData(CMFMemberTestCase.CMFMemberTestCase):

    def testMemberDataInterface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import MemberData as IMemberData
        verifyClass(IMemberData, MemberData)

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMemberDataContainer))
        suite.addTest(makeSuite(TestMemberData))
        return suite

