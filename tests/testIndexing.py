import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFMember.tests import CMFMemberTestCase

from Products.CMFPlone.tests.PloneTestCase import default_user, portal_name

"""Make sure ownership and local roles are indexed properly"""

class TestIndexing(CMFMemberTestCase.CMFMemberTestCase):

    def resultsContain(self, results, object):
        for r in results:
            if r.getObject() == object:
                return 1
        return 0
            

    def testContentIndexing(self):
        self.createUserContent()
        portal = self.getPortal()
        catalog = portal.portal_catalog
        catalog.refreshCatalog(clear=1)
        
        results = catalog.search({'indexedOwner' : '/' + portal_name + '/acl_users/' + self.portal_user.getUserName()})
        self.failUnless(self.resultsContain(results, self.portal.folder1))
        self.failUnless(self.resultsContain(results, self.portal.folder1.doc1))
        self.failUnless(self.resultsContain(results, self.portal.folder2.doc3))

        results = catalog.search({'indexedOwner': '/acl_users/' + self.root_user.getUserName()})
        self.failUnless(self.resultsContain(results, self.portal.folder2))
        self.failUnless(self.resultsContain(results, self.portal.folder1.doc2))
        self.failUnless(self.resultsContain(results, self.portal.folder2.doc4))

        results = catalog.search({'indexedUsersWithLocalRoles' : self.portal_user.getUserName()})
        self.failUnless(self.resultsContain(results, self.portal.folder2))
        
        results = catalog.search({'indexedUsersWithLocalRoles' : self.root_user.getUserName()})
        self.failUnless(self.resultsContain(results, self.portal.folder1))



if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestIndexing))
        return suite
