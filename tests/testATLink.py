"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATLink.py,v 1.3 2004/04/29 14:05:27 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

from common import *

URL='http://www.example.org/'

def editCMF(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.edit(remote_url=URL)

def editATCT(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.setRemoteUrl(URL)

tests = []

class TestATLink(ATCTTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATLink.ATLink(oid='dummy')
        self._dummy.initializeArchetype()

    def testSomething(self):
        # Test something
        self.failUnless(1==1)

    def beforeTearDown(self):
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATLink)

class TestSiteATLink(ATCTSiteTestCase):

    def afterSetUp(self):
        ATCTSiteTestCase.afterSetUp(self)
        self._portal = self.app.portal
        # login as manager
        user = self.getManagerUser()
        newSecurityManager(None, user)

        self._portal.invokeFactory(type_name='ATLink', id='ATCT')
        self._ATCT = getattr(self._portal, 'ATCT')

        self._portal.invokeFactory(type_name='Link', id='cmf')
        self._cmf = getattr(self._portal, 'cmf')

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == 'ATLink', ti.getId())
        self.failUnless(ti.Title() == 'AT Link', ti.Title())
        #self.failUnless(ti.getIcon() == 'link_icon.gif', ti.getIcon())
        self.failUnless(ti.Metatype() == 'ATLink', ti.Metatype())

    def testLink(self):
        obj = self._ATCT
        
        url = 'http://www.example.org/'
        obj.setRemoteUrl(url)
        self.failUnlessEqual(obj.getRemoteUrl(), url)
        
        url = 'false:url'
        obj.setRemoteUrl(url)
        self.failUnlessEqual(obj.getRemoteUrl(), url)

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
        url         = old.getRemoteUrl()


        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = LinkMigrator(old)
        m()

        migrated = getattr(self._portal, id)

        self.failUnless(isinstance(migrated, ATLink.ATLink),
                        migrated.__class__)
        self.failUnless(migrated.getTypeInfo().getId() == 'ATLink',
                        migrated.getTypeInfo().getId())

        self.failUnless(migrated.Title() == title, 'Title mismatch: %s / %s' \
                        % (migrated.Title(), title))
        self.failUnless(migrated.Description() == description,
                        'Description mismatch: %s / %s' % (migrated.Description(), description))
        self.failUnless(migrated.ModificationDate() == mod, 'Modification date mismatch: %s / %s' \
                        % (migrated.ModificationDate(), mod))
        self.failUnless(migrated.CreationDate() == create, 'Creation date mismatch: %s / %s' \
                        % (migrated.CreationDate(), create))

        self.failUnless(migrated.getRemoteUrl() == url, 'URL mismatch: %s / %s' \
                        % (migrated.CreationDate(), create))

    def beforeTearDown(self):
        # logout
        noSecurityManager()
        del self._ATCT
        del self._cmf
        ATCTSiteTestCase.beforeTearDown(self)


tests.append(TestSiteATLink)

class TestATLinkFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATLink.ATLink(oid='dummy')
        self._dummy.initializeArchetype()
        # more

    def test_remoteUrlField(self):
        dummy = self._dummy
        field = dummy.getField('remoteUrl')

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
        self.failUnless(field.accessor == 'getRemoteUrl',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setRemoteUrl',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        CMFCorePermissions.ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == ('isURL',),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

    def beforeTearDown(self):
        # more
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATLinkFields)

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
