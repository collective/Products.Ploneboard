"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests

$Id: testATFavorite.py,v 1.4 2004/04/29 14:05:27 tiran Exp $
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


from Products.Archetypes.ArchetypeTool import modify_fti, base_factory_type_information
from copy import deepcopy
# XXX hacking into :]
# set global_allow to 1 for testing with invokeFactory
ATFavorite.ATFavorite.global_allow = 1
# modify the FTI to enable the modification
klass = ATFavorite.ATFavorite
pkg_name = ATFavorite
fti = deepcopy(base_factory_type_information)
modify_fti(fti, klass, pkg_name)

modify_fti(fti, ATFavorite.ATFavorite, ATFavorite)

URL='/test/url'

def editCMF(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.edit(remote_url=URL)

def editATCT(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.setRemoteUrl(URL)

tests = []

class TestATFavorite(ATCTTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATFavorite.ATFavorite(oid='dummy')
        self._dummy.initializeArchetype()

    def beforeTearDown(self):
        del self._dummy
        ATCTTestCase.beforeTearDown(self)

tests.append(TestATFavorite)

class TestSiteATFavorite(ATCTSiteTestCase):

    def afterSetUp(self):
        ATCTSiteTestCase.afterSetUp(self)
        self._portal = self.app.portal
        # login as manager
        user = self.getManagerUser()
        newSecurityManager(None, user)

        self._portal.invokeFactory(type_name='ATFavorite', id='ATCT')
        self._ATCT = getattr(self._portal, 'ATCT')

        self._portal.invokeFactory(type_name='Favorite', id='cmf')
        self._cmf = getattr(self._portal, 'cmf')

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == 'ATFavorite', ti.getId())
        self.failUnless(ti.Title() == 'AT Favorite', ti.Title())
        #self.failUnless(ti.getIcon() == 'link_icon.gif', ti.getIcon())
        self.failUnless(ti.Metatype() == 'ATFavorite', ti.Metatype())

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))
        self.failUnless(old.getRemoteUrl() == new.getRemoteUrl(), 'URL mismatch: %s / %s' \
                        % (old.getRemoteUrl(), new.getRemoteUrl()))

    def testLink(self):
        obj = self._ATCT
        for url in ('', '/test/',):
            obj.setRemoteUrl(url)
            u = self._portal.portal_url()
            if url.startswith('/'):
                url = url[1:]
            if url:
                u='%s/%s' % (u, url)
            self.failUnlessEqual(obj.getRemoteUrl(), u)

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
        m = FavoriteMigrator(old)
        m(unittest=1)

        migrated = getattr(self._portal, id)

        self.failUnless(isinstance(migrated, ATFavorite.ATFavorite),
                        migrated.__class__)
        self.failUnless(migrated.getTypeInfo().getId() == 'ATFavorite',
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


tests.append(TestSiteATFavorite)

class TestATFavoriteFields(ATCTFieldTestCase):

    def afterSetUp(self):
        ATCTTestCase.afterSetUp(self)
        self._dummy = ATFavorite.ATFavorite(oid='dummy')
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
        self.failUnless(field.accessor == '_getRemoteUrl',
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
        self.failUnless(field.validators == (),
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

tests.append(TestATFavoriteFields)

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
