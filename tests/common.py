"""Common imports and declarations

common includes a set of basic things that every test needs. Ripped of from my
Archetypes test suit

$Id: common.py,v 1.7 2004/06/13 21:49:19 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

# enable nice names for True and False from newer python versions
try:
    dummy=True
except NameError: # python 2.1
    True  = 1
    False = 0

def Xprint(s):
    """print helper

    print data via print is not possible, you have to use
    ZopeTestCase._print or this function
    """
    ZopeTestCase._print(str(s)+'\n')

def dcEdit(obj):
    """dublin core edit (inplace)
    """
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    # XXX more

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

###
# general test suits including products
###
from Testing import ZopeTestCase
ZopeTestCase.installProduct('CMFCore', 1)
ZopeTestCase.installProduct('CMFDefault', 1)
ZopeTestCase.installProduct('CMFCalendar', 1)
ZopeTestCase.installProduct('CMFTopic', 1)
ZopeTestCase.installProduct('DCWorkflow', 1)
ZopeTestCase.installProduct('CMFActionIcons', 1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', 1)
ZopeTestCase.installProduct('CMFFormController', 1)
ZopeTestCase.installProduct('GroupUserFolder', 1)
ZopeTestCase.installProduct('ZCTextIndex', 1)
ZopeTestCase.installProduct('CMFPlone', 1)
ZopeTestCase.installProduct('MailHost', 1)
ZopeTestCase.installProduct('PageTemplates', 1)
ZopeTestCase.installProduct('PythonScripts', 1)
ZopeTestCase.installProduct('ExternalMethod', 1)
ZopeTestCase.installProduct('ZCatalog', 1)
ZopeTestCase.installProduct('Archetypes', 1)
ZopeTestCase.installProduct('ArchExample', 1)
ZopeTestCase.installProduct('ArchetypesTestUpdateSchema', 1)
ZopeTestCase.installProduct('PortalTransforms', 1)
ZopeTestCase.installProduct('ATContentTypes', 1)

###
# from archetypes
###

from Products.Archetypes.public import *
from Products.Archetypes.config import PKG_NAME
from Products.Archetypes.tests import ArchetypesTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.Storage import AttributeStorage, MetadataStorage
from Products.Archetypes import listTypes
from Products.Archetypes.Widget import IdWidget, StringWidget, BooleanWidget, \
     KeywordWidget, TextAreaWidget, CalendarWidget, SelectionWidget
from Products.Archetypes.utils import DisplayList
from Products.CMFCore  import CMFCorePermissions
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE,CEILING_DATE

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

###
# ATContentTypes + migration
###

from Products.ATContentTypes.types import ATDocument, ATEvent, \
    ATFavorite, ATFile, ATFolder, ATImage, ATLink, ATNewsItem

from Products.ATContentTypes.migration.ATCTMigrator import DocumentMigrator,\
    EventMigrator, FavoriteMigrator, FileMigrator, ImageMigrator, LinkMigrator,\
    NewsItemMigrator, FolderMigrator

from Products.validation import ValidationChain
EmptyValidator = ValidationChain('isEmpty')
EmptyValidator.appendSufficient('isEmpty')
TidyHTMLValidator = ValidationChain('isTidyHtmlChain')
#TidyHTMLValidator.appendSufficient('isEmpty')
TidyHTMLValidator.appendRequired('isTidyHtmlWithCleanup')
URLValidator = ValidationChain('isURL')
URLValidator.appendSufficient('isEmpty')
URLValidator.appendRequired('isURL')
RequiredURLValidator = ValidationChain('isRequiredURL')
RequiredURLValidator.appendRequired('isURL')
EmailValidator = ValidationChain('isEmailChain')
EmailValidator.appendSufficient('isEmpty')
EmailValidator.appendRequired('isEmail')
PhoneValidator = ValidationChain('isPhoneChain')
PhoneValidator.appendSufficient('isEmpty')
PhoneValidator.appendRequired('isInternationalPhoneNumber')


###
# CMF Default Types
###

from Products.CMFCore import PortalFolder
from Products.CMFDefault import Document, Favorite, File, Image, Link, NewsItem
from Products.CMFCalendar import Event

# import Interface for interface testing
try:
    import Interface
except ImportError:
    # set dummy functions and exceptions for older zope versions
    def verifyClass(iface, candidate, tentative=0):
        return True
    def verifyObject(iface, candidate, tentative=0):
        return True
    def getImplementsOfInstances(object):
        return ()
    def getImplements(object):
        return ()
    def flattenInterfaces(interfaces, remove_duplicates=1):
        return ()
    class BrokenImplementation(Exception): pass
    class DoesNotImplement(Exception): pass
    class BrokenMethodImplementation(Exception): pass
else:
    from Interface.Implements import getImplementsOfInstances, \
         getImplements, flattenInterfaces
    from Interface.Verify import verifyClass, verifyObject
    from Interface.Exceptions import BrokenImplementation, DoesNotImplement
    from Interface.Exceptions import BrokenMethodImplementation

###
# ATContentTypes tests
###
from ATCTSiteTestCase import ATCTFieldTestCase
from ATCTSiteTestCase import ATCTSiteTestCase
