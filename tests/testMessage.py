#                                                       #

#               Test Message                            #

#                                                       #



import os, sys

if __name__ == '__main__':

    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture

from Testing import ZopeTestCase


from Products.Ploneboard.Ploneboard import Ploneboard
from Products.Ploneboard.Forum import Forum
from Products.Ploneboard.Conversation import Conversation



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



class TestMessage(ZopeTestCase.ZopeTestCase):

    

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
        
        self.plone._setObject('board', Ploneboard('board'))
        self.plone.board._setObject('forum', Forum('forum'))
        self.conv = self.plone.board.forum.addConversation('conv1', 'conv1 body')
        self.catalog = self.plone.board.getInternalCatalog()


    def test_addReply(self):
        conv = self.conv
     
        m = conv.objectValues()[0]
        self.assertEqual(conv.getNumberOfMessages(), 1)
        r = m.addReply('reply1', 'body1')
        self.assertEqual(conv.getNumberOfMessages(), 2)
        # check that inReplyTo of added reply is equal to Message.id, it is in reply to
        self.assertEqual(m.getId(), r.inReplyTo())
        Log(LOG_NOTICE, "Message.addReply() is OK !")

    def test_branch(self):
        forum = self.plone.board.forum
        conv = self.conv
        
        m = conv.objectValues()[0]
        r = m.addReply('reply1', 'body1')
        r1 = r.addReply('reply2', 'body2')
        
        self.assertEqual(conv.getNumberOfMessages(), 3)
        r.branch()
        self.assertEqual(conv.getNumberOfMessages(), 1)
        Log(LOG_NOTICE, "Message.branch() is OK !")
        
    def test_appendAttachment(self):
        conv = self.conv
        msg = conv.objectValues()[0]
        
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        msg.appendAttachment(title='message', file='./Message.py')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        Log(LOG_NOTICE, "Message.appendAttachment() is OK !")
        
    def test_removeAttachment(self):
        conv = self.conv
        msg = conv.objectValues()[0]
      
        msg.appendAttachment(title='message', file='./Message.py')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        msg.removeAttachment(index=0)
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        Log(LOG_NOTICE, "Message.removeAttachment() is OK !")
        
    def test_changeAttachment(self):
        conv = self.conv
        msg = conv.objectValues()[0]
      
        msg.appendAttachment(title='message', file='./Message.py')
        old_data = str(msg.getAttachment(index=0))
        msg.changeAttachment(index=0, title='conv', file='./Conversation.py')
        self.assertEqual(msg.getAttachment(index=0).title, 'conv')
        self.assertNotEqual(str(msg.getAttachment(index=0)), old_data)
        Log(LOG_NOTICE, "Message.changeAttachment() is OK !")


if __name__ == '__main__':

    framework(descriptions=1, verbosity=1)

else:

    import unittest

    def test_suite():

        suite = unittest.TestSuite()

        suite.addTest(unittest.makeSuite(TestMessage))

        return suite



