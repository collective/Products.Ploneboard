"""ATContentTypes site tests

For tests that needs a plone portal including archetypes and portal transforms

$Id: ATCTSiteTestCase.py,v 1.12 2004/08/05 23:52:10 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import time

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base

from common import dcEdit, EmptyValidator

from Products.Archetypes.Storage import MetadataStorage
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.tests import ArchetypesTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.Extensions.Install import install as installATCT
from Products.ATContentTypes.Extensions.toolbox import isSwitchedToATCT

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
        self.failUnlessEqual(ti.getId(), self.portal_type)
        self.failUnlessEqual(ti.Title(), self.title)
        self.failUnlessEqual(ti.getIcon(), self.icon)
        self.failUnlessEqual(ti.Metatype(), self.meta_type)

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
        else:
            title = kwargs.get('title')
            description = kwargs.get('description')

        self.failUnlessEqual(first.Title(), title)
        self.failUnlessEqual(first.Description(), description)
        # XXX more

    def compareAfterMigration(self, migrated, mod=None, created=None):
        self.failUnless(isinstance(migrated, self.klass),
                        migrated.__class__)
        self.failUnlessEqual(migrated.getTypeInfo().getId(), self.portal_type)
        self.failUnlessEqual(migrated.ModificationDate(), mod)
        self.failUnlessEqual(migrated.CreationDate(), created)


    def beforeTearDown(self):
        # logout
        noSecurityManager()


class ATCTFieldTestCase(BaseSchemaTest):
    """ ATContentTypes test including AT schema tests """

    def afterSetUp(self):
        # initalize the portal but not the base schema test
        # because we want to overwrite the dummy and don't need it
        ArchetypesTestCase.ArcheSiteTestCase.afterSetUp(self)
        self.setRoles(['Manager',])

    def createDummy(self, klass, id='dummy'):
        portal = self.portal
        dummy = klass(oid=id)
        # put dummy in context of portal
        dummy = dummy.__of__(portal)
        portal.dummy = dummy
        dummy.initializeArchetype()
        return dummy

    def test_description(self):
        dummy = self._dummy
        field = dummy.getField('description')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0)
        self.failUnless(field.default == '')
        self.failUnless(field.searchable == 1)
        #XXX self.failUnless(field.primary == 0)
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
        self.failUnless(field.generateMode == 'mVc', field.generateMode)
        #self.failUnless(field.generateMode == 'veVc', field.generateMode)
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
    portal = app.portal
    if not quiet: ZopeTestCase._print('Installing ATContentTypes ... ')

    # login as manager
    user = app.acl_users.getUserById(ArchetypesTestCase.portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # add ATCT
    if hasattr(aq_base(portal), 'switchCMF2ATCT'):
        ZopeTestCase._print('already installed ... ')
    else:
        installATCT(portal)

    if isSwitchedToATCT(portal):
        # XXX right now ATCT unit tests don't run in ATCT mode.
        # Switching to native mode
        ZopeTestCase._print('switching to CMF mode ... ')
        portal.switchATCT2CMF()

    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupATCT(app)
ZopeTestCase.close(app)
