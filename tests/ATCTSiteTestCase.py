"""ATContentTypes site tests

For tests that needs a plone portal including archetypes and portal transforms

$Id: ATCTSiteTestCase.py,v 1.4 2004/05/20 12:44:50 tesdal Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import time
#from Testing import ZopeTestCase
#from AccessControl.SecurityManagement import newSecurityManager
#from AccessControl.SecurityManagement import noSecurityManager
from common import *

from Products.Archetypes.Storage import AttributeStorage, MetadataStorage
from Products.CMFCore  import CMFCorePermissions
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.tests.common import ArcheSiteTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.Extensions.Install import install as installATCT

from Products.CMFPlone.tests import PloneTestCase
portal_name = PloneTestCase.portal_name
portal_owner = PloneTestCase.portal_owner

class ATCTSiteTestCase(ArcheSiteTestCase):
    """ AT Content Types test case based on a plone site with archetypes"""
    def test_dcEdit(self):
        #if not hasattr(self, '_cmf') or not hasattr(self, '_ATCT'):
        #    return
        old = self._cmf
        new = self._ATCT
        dcEdit(old)
        dcEdit(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))
        # XXX more

class ATCTFieldTestCase(ArcheSiteTestCase, BaseSchemaTest):
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
        self.failUnless(field.validators == {'handlers': (), 'strategy': 'and'})
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnless(tuple(vocab) == ())

def setupATCT(app, quiet=0):
    get_transaction().begin()
    _start = time.time()
    if not quiet: ZopeTestCase._print('Installing ATContentTypes ... ')

    # login as manager
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
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
