import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase
from Products.CMFMember.setup.ImportMembers import importUsers
from sets import Set

class TestImport(CMFMemberTestCase.CMFMemberTestCase):

    def testSimpleCSVImport(self):
        importUsers(self, self.portal, basedir=os.path.abspath(os.path.curdir))
        mbr=dict([(x.id, x) for x in self.portal.portal_memberdata.objectValues()])
        self.assertEqual('public', self.portal.portal_workflow.getInfoFor( mbr['test1'], 'review_state') )
        self.assertEqual(Set( ['test1', 'unittest_admin', 'test3', 'test2'] ), Set(mbr.keys()))
        self.failUnless( "No portrait written", mbr['test1'].getRawPortrait() )

    def testOverwriteCSVImport(self):
        importUsers(self, self.portal, basedir=os.path.abspath(os.path.curdir))
        importUsers(self, self.portal, basedir=os.path.abspath(os.path.curdir), overwrite=True)
        
        mbr=dict([(x.id, x) for x in self.portal.portal_memberdata.objectValues()])
        self.assertEqual('public', self.portal.portal_workflow.getInfoFor( mbr['test1'], 'review_state') )
        self.assertEqual(Set( ['test1', 'unittest_admin', 'test3', 'test2'] ), Set(mbr.keys()))
        self.failUnless( "No portrait written", mbr['test1'].getRawPortrait() )
        

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestImport))
        return suite
