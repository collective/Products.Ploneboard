"""ConstrainTypesMixin

Test the ability to constrain types inside a folder

$Id: testContrainTypes.py,v 1.2 2004/08/17 16:19:59 tiran Exp $
"""

__author__ = 'Leonardo Almeida'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

from Products.ATContentTypes.config import *
from AccessControl import Unauthorized
from Products.ATContentTypes import ConstrainTypesMixin
from Products.ATContentTypes.interfaces.IConstrainTypes import IConstrainTypes
from Products.Archetypes.public import registerType, process_types, listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.CMFPlone.tests import PloneTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Testing.ZopeTestCase import user_name as default_user

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

tests = []

class TestConstrainTypes(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        #qi = self.portal.portal_quickinstaller
        #qi.installProduct('ATContentTypes')
        self.loginPortalOwner()
        self.portal.invokeFactory('ATFolder', id='af')
        self.tt = self.portal.portal_types
        # an ATCT folder
        self.af = self.portal.af
        # portal_types object for ATCT folder
        self.at = self.tt.getTypeInfo(self.af)

    def test_isMixedIn(self):
        self.failUnless(isinstance(self.af,
                                   ConstrainTypesMixin.ConstrainTypesMixin),
                        "ConstrainTypesMixin was not mixed in to ATFolder")
        self.failUnless(IConstrainTypes.isImplementedBy(self.af),
                        "IConstrainTypes not implemented by ATFolder instance")

    def test_unconstrained(self):
        # unlimited types at portal_types tool
        # no portal_type filtered at object
        af = self.af
        at = self.at
        at.manage_changeProperties(filter_content_types=False)
        self.failIf(at.filter_content_types,
                    "ContentTypes are still being filtered at factory")
        af.setLocallyAllowedTypes([])
        possible_types_ids = [fti.id for fti in af._getPossibleTypes()]
        self.failIf('ATImage' not in possible_types_ids,
                    'ATImage not available to be filtered!')
        allowed_ids = [fti.id for fti in af.allowedContentTypes()]
        self.failIf('ATImage' not in allowed_ids,
                    'ATImage not available to add!')
        af.invokeFactory('ATImage', id='anATImage')
        afi = af.anATImage # will bail if invokeFactory didn't work
        self.failIf('ATDocument' not in possible_types_ids,
                    'ATDocument not available to add!')
        af.invokeFactory('ATDocument', id='anATDocument')
        afd = af.anATDocument # will bail if invokeFactory didn't work

    def test_constrained(self):
        af = self.af
        at = self.at
        at.manage_changeProperties(filter_content_types=False)
        self.failIf(at.filter_content_types,
                    "ContentTypes are still being filtered at factory")
        af.setLocallyAllowedTypes(['ATImage'])
        allowed_ids = [fti.id for fti in af.allowedContentTypes()]
        af.invokeFactory('ATImage', id='anATImage')
        afi = af.anATImage # will bail if invokeFactory didn't work
        self.assertEquals(allowed_ids, ['ATImage'])
        self.assertRaises(ValueError, af.invokeFactory,
                          'ATDocument', id='anATDocument')

    def test_ftiInteraction(self):
        af = self.af
        at = self.at
        tt = self.tt
        af_allowed_types = ['ATDocument', 'ATImage',
                            'ATFile', 'ATFolder',
                            'Folder']
        af_allowed_types.sort()
        at.manage_changeProperties(filter_content_types=True,
                                   allowed_content_types=af_allowed_types)
        af.setLocallyAllowedTypes([])
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(af_allowed_types, af_local_types)
        #                  "fti allowed types don't match local ones")
        # let's limit locally and see what happens
        types1 = ['ATImage', 'ATFile', 'ATFolder', 'Folder']
        types1.sort()
        af.setLocallyAllowedTypes(types1)
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(types1, af_local_types,
                          "constrained types don't match local ones")
        # now let's unlimit globally to see if the local constrains remain
        at.manage_changeProperties(filter_content_types=False)
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(types1, af_local_types,
                          "constrained types don't match local ones")
        # now let's see if inheritance kicks in even thru a non
        # constrained type
        af.invokeFactory('Folder', id='nf')
        af.nf.invokeFactory('Folder', id='bf')
        bf = af.nf.bf
        bf_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        bf_local_types.sort()
        self.assertEquals(types1, bf_local_types,
                          "constrained types don't match inherited ones")

    def test_unconstrainedButUnauthorized(self):
        user = self.portal.portal_membership.getMemberById(default_user)
        newSecurityManager(None, user)
        af = self.portal.af
        # should not raise ValueError
        self.assertRaises(Unauthorized,
                          af.invokeFactory, 'ATFolder', id='bf')

tests.append(TestConstrainTypes)

import unittest
def test_suite():
    # framework.py test_suite is trying to run ATCT*TestCase
    # so we have to provide our own
    suite = unittest.TestSuite()
    if not ENABLE_CONSTRAIN_TYPES_MIXIN:
        # we can only run tests if ConstrainedTypesMixin is enabled
        # return an empty suite otherwise
        return suite
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
