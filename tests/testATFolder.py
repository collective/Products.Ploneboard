"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATFolder.py,v 1.3 2004/05/15 01:54:07 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

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
        # login as manager
        user = self.getManagerUser()
        newSecurityManager(None, user)

        self._portal.invokeFactory(type_name='ATFolder', id='ATCT')
        self._ATCT = getattr(self._portal, 'ATCT')

        self._portal.invokeFactory(type_name='Folder', id='cmf')
        self._cmf = getattr(self._portal, 'cmf')

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == 'ATFolder', ti.getId())
        self.failUnless(ti.Title() == 'AT Folder', ti.Title())
        #self.failUnless(ti.getIcon() == 'folder_icon.gif', ti.getIcon())
        self.failUnless(ti.Metatype() == 'ATFolder', ti.Metatype())

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()
        
        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        create      = old.CreationDate()

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = FolderMigrator(old)
        m(unittest=1)

        migrated = getattr(self._portal, id)

        self.failUnless(isinstance(migrated, ATFolder.ATFolder),
                        migrated.__class__)
        self.failUnless(migrated.getTypeInfo().getId() == 'ATFolder',
                        migrated.getTypeInfo().getId())

        self.failUnless(migrated.Title() == title, 'Title mismatch: %s / %s' \
                        % (migrated.Title(), title))
        self.failUnless(migrated.Description() == description,
                        'Description mismatch: %s / %s' % (migrated.Description(), description))
        self.failUnless(migrated.ModificationDate() == mod, 'Modification date mismatch: %s / %s' \
                        % (migrated.ModificationDate(), mod))
        self.failUnless(migrated.CreationDate() == create, 'Creation date mismatch: %s / %s' \
                        % (migrated.CreationDate(), create))


    def beforeTearDown(self):
        del self._ATCT
        del self._cmf
        ATCTSiteTestCase.beforeTearDown(self)

tests.append(TestSiteATFolder)

class TestATFolderFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTFieldTestCase.afterSetUp(self)
        self._dummy = ATFolder.ATFolder(oid='dummy')
        self._dummy.initializeArchetype()
        # wrap dummy object in the acquisition context of the site
        site = self.getPortal()
        self._dummy = self._dummy.__of__(site)
        # more

    def test_somefield(self):
        # Test a field
        dummy = self._dummy
        field = dummy.getField('somefield')
        self.failUnless(1==1)

    def beforeTearDown(self):
        # more
        ATCTFieldTestCase.beforeTearDown(self)

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
