#
# PloneTestCase
#

# $Id: atse_testcase.py,v 1.1 2004/09/18 02:24:09 brcwhit Exp $

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('ATSchemaEditorNG')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('generator')
ZopeTestCase.installProduct('validation')
ZopeTestCase.installProduct('PortalTransforms')

def makeContent( container, portal_type, id='document', **kw ):
    container.invokeFactory( type_name=portal_type, id=id )
    return getattr( container, id )

class ATSETestCase( PloneTestCase.PloneTestCase ):
    '''TestCase for ATSchemaEditorNG testing'''

    dependencies=('Archetypes', 'ATSchemaEditorNG')

    def installProducts(self, products):
        self.portal.portal_quickinstaller.installProducts(products=products, stoponerror=1)

    def installDependencies(self):
        self.installProducts(self.dependencies)

    def createBasicSetup(self):
        """ basic schema editing setup """

        self.container = makeContent(self.folder, 'Container', id='container')
        self.target1 = makeContent(self.container, 'Target1', id='target1')
        self.target2 = makeContent(self.container, 'Target2', id='target2')
        
