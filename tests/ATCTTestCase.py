"""ATContentTypes tests

$Id: ATCTTestCase.py,v 1.2 2004/05/15 00:51:34 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest

from Products.Archetypes.Storage import AttributeStorage, MetadataStorage
from Products.CMFCore  import CMFCorePermissions
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.interfaces.layer import ILayerContainer

class ATCTTestCase(ZopeTestCase.ZopeTestCase):
    """ ATContentTypes test case based on ZopeTestCase"""

class ATCTFieldTestCase(ATCTTestCase, BaseSchemaTest):
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

