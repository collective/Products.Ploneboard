#
# PloneTestCase
#

# $Id: atse_testcase.py,v 1.2 2004/11/07 21:52:51 brcwhit Exp $

from Testing import ZopeTestCase
### ought to be refactored to use CMFTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.public import listTypes
from Products.ATSchemaEditorNG.config import *

from StringIO import StringIO

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
        out = StringIO()
        installTypes(self.portal, out, listTypes(PKG_NAME), PKG_NAME)
        
        self.container = makeContent(self.folder, 'Container', id='container')
        self.target1 = makeContent(self.container, 'Target1', id='target1')
        self.target2 = makeContent(self.container, 'Target2', id='target2')

