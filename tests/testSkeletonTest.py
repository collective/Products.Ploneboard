"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testSkeletonTest.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

tests = []

class TestATSomething(ATCTTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        # more

    def testSomething(self):
        # Test something
        self.failUnless(1==1)

    def beforeTearDown(self):
        # more
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATSomething)

class TestATSomethingFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATSomething.ATSomething(oid='dummy')
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

#tests.append(TestATSomethingFields)

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
