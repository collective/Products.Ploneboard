#                                                       #
#               Test Ploneboard                         #
#                                                       #

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture
from Testing import ZopeTestCase

from Products.Ploneboard.Ploneboard import Ploneboard

# Install CMF/Plone products
ZopeTestCase.installProduct('ExternalMethod')
ZopeTestCase.installProduct('PageTemplates')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('MailHost')

# Install our product
ZopeTestCase.installProduct('Ploneboard')


# Set log options if Log module is available
# This is done to set LOG_PROCESSORs to file logs instead of Zope logs
try:
    import Log

    Log.LOG_LEVEL = Log.LOG_DEBUG

    Log.LOG_PROCESSOR = {
        Log.LOG_NONE: Log.logFile,
        Log.LOG_CRITICAL: Log.logFile,
        Log.LOG_ERROR: Log.logFile,
        Log.LOG_WARNING: Log.logFile,
        Log.LOG_NOTICE: Log.logFile,
        Log.LOG_DEBUG: Log.logFile,
        }

    from Log import *
    Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))

except:
    print "Log module not available"
    LOG_DEBUG = None
    LOG_NOTICE = None
    LOG_WARNING = None
    LOG_ERROR = None
    LOG_CRITICAL = None
    def Log(*args, **kw):
        pass
    raise


class TestPloneboard(ZopeTestCase.ZopeTestCase):

  
    def afterSetUp(self,):
        """
        afterSetUp(self) => This method is called to create an empty Plone Site with a Ploneboard inside you're gonna play with.

        It also joins three users called 'user1', 'user2' and 'user3'.

        And, eventually, it installs the CMFType with an external method.
        """
        # Create Plone instance
        self.folder.manage_addProduct['CMFPlone'].manage_addSite(
            id = 'plonesite',
            title = 'Sample Plone website',
            description = 'This is a sample Plone website meant to be used in a ZopeTestCase',
            email_from_address='postmaster@localhost',
            email_from_name='Portal Administrator',
            validate_email=0,
            custom_policy='',
            RESPONSE=None)
        self.plone = self.folder.plonesite
        
        # Now, installs our product's type
        self.plone.manage_addProduct['ExternalMethod'].manage_addExternalMethod(
            id='ploneboard',
            title="Install Ploneboard",
            module="Ploneboard.Install",
            function="install"
            )
        ExMethod = self.plone.restrictedTraverse('ploneboard')
        ExMethod()
    

    def test_addPloneboard(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        # Content creation
        content_id = "board"
        self.plone.invokeFactory(
            type_name = 'Ploneboard',
            id = content_id
            )
        self.failUnless(content_id in self.plone.objectIds(), "Ploneboard has not been created or not with the right id")
        content = getattr(self.plone, content_id)

        # Basic checks
        self.assertEqual(content.title, '')
        self.assertEqual(content.id, content_id)

        # Youpie
        Log(LOG_NOTICE, "Ploneboard instanciated correctly !")
        
    def test_removePloneboard(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        # Content creation
        content_id = "board"
        self.plone.invokeFactory(
            type_name = 'Ploneboard',
            id = content_id
            )
        self.failUnless(content_id in self.plone.objectIds(), "Ploneboard has not been created or not with the right id")
        content = getattr(self.plone, content_id)
        
        self.plone._delObject(content_id)
        self.assertEqual(len(self.plone.contentValues('Ploneboard')), 0)
        
        Log(LOG_NOTICE, "Ploneboard removed correctly !")


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboard))
        return suite

