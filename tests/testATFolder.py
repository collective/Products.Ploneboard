"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATFolder.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

tests = []

class TestATFolder(ATCTTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATFolder.ATFolder(oid='dummy')
        self._dummy.initializeArchetype()

    def testSomething(self):
        # Test something
        self.failUnless(1==1)

    def beforeTearDown(self):
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATFolder)

class TestSiteATFolder(ATCTSiteTestCase):

    def afterSetUp(self):
        ATCTSiteTestCase.afterSetUp(self)
        self._portal = self.app.portal
        ATCT = ATFolder.ATFolder(oid='ATCT')
        ATCT.initializeArchetype()
        self._portal._setObject('ATCT', ATCT)
        self._ATCT = getattr(self._portal, 'ATCT')

        cmf = PortalFolder.PortalFolder(id='cmf')
        self._portal._setObject('cmf', cmf)
        self._cmf = getattr(self._portal, 'cmf')

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == 'ATFolder', ti.getId())
        self.failUnless(ti.Title() == 'AT Folder', ti.Title())
        #self.failUnless(ti.getIcon() == 'folder_icon.gif', ti.getIcon())
        self.failUnless(ti.Metatype() == 'ATFolder', ti.Metatype())

    def beforeTearDown(self):
        del self._ATCT
        del self._cmf
        ATCTSiteTestCase.beforeTearDown(self)

tests.append(TestSiteATFolder)

class TestATFolderFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATFolder.ATFolder(oid='dummy')
        self._dummy.initializeArchetype()
        # more

    def test_somefield(self):
        # Test a field
        dummy = self._dummy
        field = dummy.getField('somefield')
        self.failUnless(1==1)

    def beforeTearDown(self):
        # more
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATFolderFields)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
