"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATDocument.py,v 1.4 2004/04/29 14:05:27 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

example_stx = """
Header

 Text, Text, Text
 
   * List
   * List
"""

def editCMF(obj):
    text_format='stx'
    dcEdit(obj)
    obj.edit(text_format = text_format, text = example_stx)

def editATCT(obj):
    text_format='text/structured'
    dcEdit(obj)
    obj.setText(example_stx, mimetype = text_format)

tests = []

class TestATDocument(ATCTTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATDocument.ATDocument(oid='dummy')
        self._dummy.initializeArchetype()

    def testSomething(self):
        # Test something
        self.failUnless(1==1)

    def beforeTearDown(self):
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATDocument)

class TestSiteATDocument(ATCTSiteTestCase):

    def afterSetUp(self):
        ATCTSiteTestCase.afterSetUp(self)
        self._portal = self.app.portal
        # login as manager
        user = self.getManagerUser()
        newSecurityManager(None, user)

        self._portal.invokeFactory(type_name='ATDocument', id='ATCT')
        self._ATCT = getattr(self._portal, 'ATCT')

        self._portal.invokeFactory(type_name='Document', id='cmf')
        self._cmf = getattr(self._portal, 'cmf')

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == 'ATDocument', ti.getId())
        self.failUnless(ti.Title() == 'AT Document', ti.Title())
        #self.failUnless(ti.getIcon() == 'document_icon.gif', ti.getIcon())
        self.failUnless(ti.Metatype() == 'ATDocument', ti.Metatype())
        
    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.CookedBody() == new.CookedBody(), 'Body mismatch: %s / %s' \
                        % (old.CookedBody(), new.CookedBody()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()
        
        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        create      = old.CreationDate()
        body        = old.CookedBody()

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = DocumentMigrator(old)
        m(unittest=1)
        get_transaction().commit(1)

        migrated = getattr(self._portal, id)

        self.failUnless(isinstance(migrated, ATDocument.ATDocument),
                        migrated.__class__)
        self.failUnless(migrated.getTypeInfo().getId() == 'ATDocument',
                        migrated.getTypeInfo().getId())

        self.failUnless(migrated.Title() == title, 'Title mismatch: %s / %s' \
                        % (migrated.Title(), title))
        self.failUnless(migrated.Description() == description,
                        'Description mismatch: %s / %s' % (migrated.Description(), description))
        self.failUnless(migrated.ModificationDate() == mod, 'Modification date mismatch: %s / %s' \
                        % (migrated.ModificationDate(), mod))
        self.failUnless(migrated.CreationDate() == create, 'Creation date mismatch: %s / %s' \
                        % (migrated.CreationDate(), create))

        self.failUnless(migrated.CookedBody() == body, 'Body mismatch: %s / %s' \
                        % (migrated.CookedBody(), body))

    def beforeTearDown(self):
        # logout
        noSecurityManager()
        del self._ATCT
        del self._cmf
        ATCTSiteTestCase.beforeTearDown(self)

tests.append(TestSiteATDocument)

class TestATDocumentFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATDocument.ATDocument(oid='dummy')
        self._dummy.initializeArchetype()

    def test_textField(self):
        dummy = self._dummy
        field = dummy.getField('text')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (), 
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0, 
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        CMFCorePermissions.ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'text', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == ('isTidyHtmlWithCleanup',),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type == 'text/restructured',
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/html',
                        'Value is %s' % field.default_output_type)
        self.failUnless(field.allowable_content_types == ('text/structured',
                        'text/restructured', 'text/html', 'text/plain', 
                        'text/plain-pre', 'text/python-source'),
                        'Value is %s' % str(field.allowable_content_types))

    def beforeTearDown(self):
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATDocumentFields)

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
