"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATFile.py,v 1.11 2005/01/24 18:27:01 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests.common import *

file_text = """
foooooo
"""

def editCMF(obj):
    dcEdit(obj)
    obj.edit(file=file_text)

def editATCT(obj):
    dcEdit(obj)
    obj.edit(file=file_text)
    #XXX obj.setFormat('text/plain')

tests = []

class TestSiteATFile(ATCTSiteTestCase):

    klass = ATFile.ATFile
    portal_type = 'ATFile'
    title = 'AT File'
    meta_type = 'ATFile'
    icon = 'file_icon.gif'

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.compareDC(old, new)
        self.failUnlessEqual(str(old), str(new.getFile()))

    def testCompatibilityFileAccess(self):
        new = self._ATCT
        editATCT(new)
        # test for crappy access ways of CMF :)
        self.failUnlessEqual(str(new), file_text)
        self.failUnlessEqual(new.data, file_text)
        self.failUnlessEqual(str(new.getFile()), file_text)
        self.failUnlessEqual(new.getFile().data, file_text)
        self.failUnlessEqual(new.get_data(), file_text)

    def testCompatibilityContentTypeAccess(self):
        new = self._ATCT
        editATCT(new)
        # XXX todo

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()
        file        = str(old)

        time.sleep(1.5)

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = FileMigrator(old)
        m(unittest=1)

        migrated = getattr(self._portal, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        self.failUnlessEqual(file, str(migrated.getFile()))
        self.failIfEqual(migrated.data, None)
        self.failIfEqual(migrated.data, '')
        # XXX more

    def beforeTearDown(self):
        del self._ATCT
        del self._cmf
        ATCTSiteTestCase.beforeTearDown(self)

tests.append(TestSiteATFile)

class TestATFileFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATFile.ATFile)

    def test_fileField(self):
        dummy = self._dummy
        field = dummy.getField('file')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getFile',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setFile',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        CMFCorePermissions.ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'file', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == "(('checkFileMaxSize', V_REQUIRED))",
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, FileWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

    def beforeTearDown(self):
        # more
        ATCTFieldTestCase.beforeTearDown(self)

tests.append(TestATFileFields)

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
