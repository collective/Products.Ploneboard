"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests


"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests.common import *

example_stx = """
Header

 Text, Text, Text

   * List
   * List
"""

example_rest = """
Header
======

Text, text, text

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

class TestSiteATDocument(ATCTSiteTestCase):

    klass = ATDocument.ATDocument
    portal_type = 'ATDocument'
    title = 'AT Document'
    meta_type = 'ATDocument'
    icon = 'document_icon.gif'

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.CookedBody() == new.CookedBody(), 'Body mismatch: %s / %s' \
                        % (old.CookedBody(), new.CookedBody()))

    def test_cmf_edit_failure(self):
        self._ATCT.edit(thisisnotcmfandshouldbeignored=1)

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()
        body        = old.CookedBody()

        time.sleep(1.5)

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = DocumentMigrator(old)
        m(unittest=1)
        get_transaction().commit(1)

        migrated = getattr(self._portal, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        self.failUnless(migrated.CookedBody() == body, 'Body mismatch: %s / %s' \
                        % (migrated.CookedBody(), body))

    def test_rename(self):
        doc = self._ATCT
        doc.setText(example_rest, mimetype="text/x-rst")
        self.failUnless(str(doc.getField('text').getContentType(doc)) == "text/x-rst")
        #make sure we have _p_jar
        get_transaction().commit(1)

        cur_id = 'ATCT'
        new_id = 'WasATCT'
        self._portal.manage_renameObject(cur_id, new_id)
        doc = getattr(self._portal, new_id)
        self.failUnless(str(doc.getField('text').getContentType(doc)) == "text/x-rst")


tests.append(TestSiteATDocument)

class TestATDocumentFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATDocument.ATDocument)

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
        self.failUnless(field.validators == TidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type == 'text/html',
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/html',
                        'Value is %s' % field.default_output_type)
        self.failUnless(field.allowable_content_types == ('text/structured',
                        'text/restructured', 'text/html', 'text/plain',
                        'text/plain-pre', 'text/python-source'),
                        'Value is %s' % str(field.allowable_content_types))

    def beforeTearDown(self):
        ATCTFieldTestCase.beforeTearDown(self)

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
