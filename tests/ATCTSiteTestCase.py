"""ATContentTypes site tests

For tests that needs a plone portal including archetypes and portal transforms

$Id: ATCTSiteTestCase.py,v 1.7 2004/06/13 21:49:19 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import time

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from common import dcEdit, EmptyValidator

from Products.Archetypes.Storage import AttributeStorage, MetadataStorage
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.tests import ArchetypesTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.Extensions.Install import install as installATCT

from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore as IMutableDublinCore

from Products.CMFPlone.tests import PloneTestCase
portal_name = PloneTestCase.portal_name
portal_owner = PloneTestCase.portal_owner

class ATCTSiteTestCase(ArchetypesTestCase.ArcheSiteTestCase):
    """ AT Content Types test case based on a plone site with archetypes"""
    
    klass = None
    portal_type = ''
    title = ''
    meta_type = ''
    icon = ''
    
    def afterSetUp(self):
        self._portal = self.app.portal
        # login as manager
        user = self.getManagerUser()
        newSecurityManager(None, user)
        
        ttool = getToolByName(self._portal, 'portal_types')
        atctFTI = ttool.getTypeInfo(self.portal_type)
        cmfFTI = ttool.getTypeInfo(self.klass.newTypeFor[0])
        
        atctFTI.constructInstance(self._portal, 'ATCT')
        self._ATCT = getattr(self._portal, 'ATCT')

        cmfFTI.constructInstance(self._portal, 'cmf')
        self._cmf = getattr(self._portal, 'cmf')

    def test_dcEdit(self):
        #if not hasattr(self, '_cmf') or not hasattr(self, '_ATCT'):
        #    return
        old = self._cmf
        new = self._ATCT
        dcEdit(old)
        dcEdit(new)
        self.compareDC(old, new)

    def testTypeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnless(ti.getId() == self.portal_type, ti.getId())
        self.failUnless(ti.Title() == self.title, ti.Title())
        self.failUnless(ti.getIcon() == self.icon, ti.getIcon())
        self.failUnless(ti.Metatype() == self.meta_type, ti.Metatype())

    def testDoesImplemendDC(self):
        self.failUnless(IDublinCore.isImplementedBy(self._ATCT))
        self.failUnless(IMutableDublinCore.isImplementedBy(self._ATCT))
        
    def testDoesImplementATCT(self):
        self.failUnless(IATContentType.isImplementedBy(self._ATCT))

    def compareDC(self, first, second=None, **kwargs):
        """
        """
        if second:
            title = second.Title()
            description = second.Description()
            mod = second.ModificationDate()
            created = second.CreationDate()
        else:
            title = kwargs.get('title')
            description = kwargs.get('description')
            mod = kwargs.get('mod')
            created = kwargs.get('created')
            
        time.sleep(1)
        self.failUnless(first.Title() == title, 'Title mismatch: %s / %s' \
                        % (first.Title(), title))
        self.failUnless(first.Description() == description,
                        'Description mismatch: %s / %s' % (first.Description(), description))
        self.failUnless(first.ModificationDate() == mod, 'Modification date mismatch: %s / %s' \
                        % (first.ModificationDate(), mod))
        self.failUnless(first.CreationDate() == created, 'Creation date mismatch: %s / %s' \
                        % (first.CreationDate(), created))
        # XXX more

    def compareAfterMigration(self, migrated):
        self.failUnless(isinstance(migrated, self.klass),
                        migrated.__class__)
        self.failUnless(migrated.getTypeInfo().getId() == self.portal_type,
                        migrated.getTypeInfo().getId())

    def beforeTearDown(self):
        # logout
        noSecurityManager()


class ATCTFieldTestCase(ArchetypesTestCase.ArcheSiteTestCase, BaseSchemaTest):
    """ ATContentTypes test including AT schema tests """
    
    def test_description(self):
        dummy = self._dummy
        field = dummy.getField('description')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0)
        self.failUnless(field.default == '')
        self.failUnless(field.searchable == 1)
        vocab = field.vocabulary
        self.failUnless(vocab == ())
        self.failUnless(field.enforceVocabulary == 0)
        self.failUnless(field.multiValued == 0)
        self.failUnless(field.isMetadata == 0)
        self.failUnless(field.accessor == 'Description')
        self.failUnless(field.mutator == 'setDescription')
        self.failUnless(field.read_permission == CMFCorePermissions.View)
        self.failUnless(field.write_permission ==
                        CMFCorePermissions.ModifyPortalContent)
        #XXX self.failUnless(field.generateMode == 'mVc', field.generateMode)
        self.failUnless(field.generateMode == 'veVc', field.generateMode)
        self.failUnless(field.force == '')
        self.failUnless(field.type == 'text')
        self.failUnless(isinstance(field.storage, MetadataStorage))
        self.failUnless(field.getLayerImpl('storage') == MetadataStorage())
        self.failUnless(field.validators == EmptyValidator)
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnless(tuple(vocab) == ())

def setupATCT(app, quiet=0):
    get_transaction().begin()
    _start = time.time()
    print "Installing at content types"
    if not quiet: ZopeTestCase._print('Installing ATContentTypes ... ')

    # login as manager
    user = app.acl_users.getUserById(ArchetypesTestCase.portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # add Archetypes
    installATCT(app.portal)
    
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupATCT(app)
ZopeTestCase.close(app)
