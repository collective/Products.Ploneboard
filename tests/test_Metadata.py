"""
Tests for CMFMetadata

$Id: test_Metadata.py,v 1.1 2004/02/08 16:30:37 k_vertigo Exp $
"""
import Zope
Zope.startup()

from unittest import TestCase, TestSuite, makeSuite, main

from cStringIO import StringIO

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Annotations.AnnotationTool import AnnotationTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.utils import getToolByName
from Products.Formulator import StandardFields
from Products.Formulator.TALESField import TALESMethod
from Products.CMFMetadata.MetadataTool import MetadataTool
from stubs import SecurityPolicyStub, AnonymousUserStub

SET_ID = 'ut_md'

def setupTools(root):
    root._setObject('portal_types', TypesTool())
    root._setObject('portal_annotations', AnnotationTool())
    root._setObject('portal_metadata', MetadataTool())
    root._setObject('portal_catalog', CatalogTool())

def setupContentTypes(context):
    types_tool = getToolByName(context, 'portal_types')
    types_tool._setObject('Folder', FTI(id='Folder',
                                        title='Folder or Directory',
                                        meta_type=PortalFolder.meta_type,
                                        product='CMFCore',
                                        factory='manage_addPortalFolder',
                                        filter_content_types=0)
                             )

def setupContentTree(container):
    ttool = getToolByName(container, 'portal_types')
    ttool.constructContent('Folder', container, 'zoo')

    zoo = container._getOb('zoo')

    ttool.constructContent('Folder', zoo, 'mammals')
    ttool.constructContent('Folder', zoo, 'reptiles')

    mammals = zoo._getOb('mammals')
    reptiles = zoo._getOb('reptiles')

    return zoo

def setupCatalog(context):
    catalog = getToolByName(context, 'portal_catalog')
    pass

def setupMetadataSet(context):
    mtool = getToolByName(context, 'portal_metadata')
    collection = mtool.getCollection()
    collection.addMetadataSet(SET_ID,
                              'tmd',
                              'http://www.example.com/xml/test_md')
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('Title',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )
    set.addMetadataElement('Description',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )
    element = set.getElement('Description')
    element.field._edit({'required':0})
    element.editElementPolicy(acquire_p = 1)
    return set

def setupExtendedMetadataSet(context):
    # add some additional metadata fields
    pm = getToolByName(context, 'portal_metadata')
    collection = pm.getCollection()
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('ModificationDate',
                           StandardFields.DateTimeField.meta_type,
                           'DateIndex',
                           1
                           )
    element = set.getElement('ModificationDate')
    element.field._edit_tales({'default':
                        TALESMethod('content/bobobase_modification_time')})
    element.field._edit({'required':0})
    set.addMetadataElement('Languages',
                           StandardFields.LinesField.meta_type,
                           'KeywordIndex',
                           1
                           )
    element = set.getElement('Languages')
    element.field._edit({'required':0})
    ######
    set.initialize()

def setupMetadataMapping(context):
    mtool = getToolByName(context, 'portal_metadata')
    mapping = mtool.getTypeMapping()
    mapping.setDefaultChain('ut_md')


class MetadataTests(SecurityTest):

    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root =  self.connection.root()['Application']
        newSecurityManager(None, AnonymousUserStub().__of__(self.root))
        setupTools(self.root)
        setupCatalog(self.root)
        setupContentTypes(self.root)
        setupMetadataSet(self.root)
        setupMetadataMapping(self.root)
        setupContentTree(self.root)
        self.root.REQUEST = {}

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()

class TestSetImportExport(MetadataTests):

    def testImportExport(self):
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        xml = set.exportXML()
        xmlio = StringIO(xml)
        collection.manage_delObjects([SET_ID])
        collection.importSet(xmlio)
        set = collection.getMetadataSet(SET_ID)
        xml2 = set.exportXML()
        assert xml == xml2, "Import/Export disjoint"


class TestObjectImportExport(MetadataTests):

    def testImportExport(self):
        from Products.ParsedXML.ParsedXML import createDOMDocument
        from Products.CMFMetadata.Import import import_metadata

        pm = getToolByName(self.root, 'portal_metadata')
        setupExtendedMetadataSet(self.root)
        zoo = self.root.zoo
        mammals = zoo.mammals
        binding = pm.getMetadata(zoo)
        values = binding.get(SET_ID)
        lines = """
        english
        hebrew
        swahili
        urdu
        """
        values.update(
            {'Title':'hello world',
             'Description':'cruel place',
             'Languages':lines }
            )
        binding.setValues(SET_ID, values)
        xml = "<folder>%s</folder>" % binding.renderXML(SET_ID)
        dom = createDOMDocument(xml)
        import_metadata(mammals, dom.childNodes[0])
        mammals_binding = pm.getMetadata(mammals)
        mammal_values = binding.get(SET_ID)
        for k in values.keys():
            self.assertEqual(values[k], mammal_values[k],
                             "Object Import/Export disjoint")

        xml2 = "<folder>%s</folder>" % mammals_binding.renderXML(SET_ID)
        xml_list = xml.splitlines()
        xml2_list = xml2.splitlines()
        for x in xml2_list:
            self.assert_(x in xml_list, "Object Import Export disjoin")
        for x in xml_list:
            self.assert_(x in xml2_list, "Object Import Export disjoin")


class TestCataloging(MetadataTests):
    pass


class TestMetadataElement(MetadataTests):

    def testGetDefault(self):
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Title')
        element.field._edit_tales({'default':
                                   TALESMethod('content/getPhysicalPath')})
        zoo = self.root.zoo
        binding = pm.getMetadata(zoo)
        defaults = set.getDefaults(content = zoo)
        self.assertEqual(defaults['Title'],
                         zoo.getPhysicalPath(),
                         "Tales Context Passing Failed")

    def testGetDefaultWithTalesDelegate(self):
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        zoo = self.root.zoo
        test_value = 'Rabbits4Ever'
        binding = pm.getMetadata(zoo)
        binding.setValues(SET_ID, {'Title':test_value})
        element = set.getElement('Description')
        # yikes, narly tales expression
        method = "python: content.portal_metadata.getMetadata(content).get(" \
                 "'%s', 'Title', no_defaults=1)" % SET_ID
        element.field._edit_tales({'default': TALESMethod(method)})
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value,
                         "Tales delegate for default didn't work")
         # make sure the right cached value was stored.
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value, "Wrong Data Object Cached")

    def testAcquisitionInvariant(self):
        # invariant == can't be required and acquired
        from Products.CMFMetadata.Exceptions import ConfigurationError
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Description')
        try:
            element.field._edit({'required':1})
            element.editElementPolicy(acquire_p = 1)
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed")
        try:
            element.field._edit({'required':0})
            element.editElementPolicy(acquire_p = 1)
            element.field._edit({'required':1})
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed 2")


class TestAdvancedMetadata(MetadataTests):
    """Tests for runtime binding methods"""

    def setupAcquiredMetadata(self):
        zoo = self.root.zoo
        binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        set_id = SET_ID
        binding.setValues(set_id, {'Title':'hello world',
                                   'Description':'cruel place'})

    def testContainmentAcquisitionValue(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        set_id = SET_ID
        assert m_binding[set_id]['Description'] == \
               z_binding[set_id]['Description']
        assert m_binding.get(set_id, 'Description', acquire=0) != \
               z_binding[set_id]['Description']

    def testContainmentAcquisitionList(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        set_id = SET_ID
        acquired = m_binding.listAcquired()
        # test the contained's list acquired
        self.assertEqual(len(acquired), 1)
        self.assertEqual(acquired[0][1], 'Description')
        # test the container's listacquired
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)
        # special case for
        z_binding.setValues(set_id, {'Title':'', 'Description':''})
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)

    def testObjectDelegation(self):
        from Acquisition import Implicit
        class Delegator(Implicit):
            def __init__(self, name):
                self.name = name
            def __call__(self):
                ob = self.aq_inner.aq_parent
                return getattr(ob, self.name)

        zoo = self.root.zoo
        delegate = Delegator('reptiles')
        zoo.delegate = delegate
        mams = zoo.mammals
        reps = zoo.reptiles
        r_binding = getToolByName(reps, 'portal_metadata').getMetadata(reps)
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        r_binding.setValues(SET_ID,
                            {'Title':'snake food',
                             'Description':'yummy n the tummy'}
                            )
        m_binding.setObjectDelegator('delegate')
        self.assertEqual(
            m_binding[SET_ID]['Title'],
            r_binding[SET_ID]['Title']
            )
        m_binding.clearObjectDelegator()
        assert m_binding[SET_ID]['Title'] != r_binding[SET_ID]['Title']

    def testMutationTriggerDelegation(self):
        class MutationTrigger:
            def __init__(self):
                self.called = 0
            def __call__(self):
                self.called += 1

        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        trigger = MutationTrigger()
        zoo.trigger = trigger
        m_binding.setMutationTrigger(SET_ID, 'Title', 'trigger')
        m_binding.setValues(SET_ID, {'Title':'surfin betty',
                                     'Description':'morning pizza'})
        self.assertEqual(trigger.called, 1)
        m_binding.setValues(SET_ID, {'Description':'midnight raid'})
        self.assertEqual(trigger.called, 1)
        m_binding.clearMutationTrigger(SET_ID)
        # props to tennyson
        m_binding.setValues(SET_ID,
                            {'Title':
                             'To strive, to seek, to find, and not to yield'}
                            )
        self.assertEqual(trigger.called, 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetImportExport))
    suite.addTest(makeSuite(TestObjectImportExport))
    suite.addTest(makeSuite(TestCataloging))
    suite.addTest(makeSuite(TestMetadataElement))
    suite.addTest(makeSuite(TestAdvancedMetadata))
    return suite


if __name__ == '__main__':
    main()

