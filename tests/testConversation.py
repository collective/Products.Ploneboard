#                                                       #
#               Test Conversation                              #
#                                                       #

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.Ploneboard.Ploneboard import Ploneboard
from Products.Ploneboard.Forum import Forum

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

class TestConversation(ZopeTestCase.ZopeTestCase):
    
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
        self.catalog = self.plone.board.getInternalCatalog()

    def test_addConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        
        forum = self.plone.board.forum

        self.assertEqual(len(forum.contentValues('Conversation')), 0)
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        self.assertEqual(len(forum.contentValues('Conversation')), 1)

        self.failUnless(conv_id in forum.objectIds())

        self.assertEqual(conv.Title(), 'subject')
     
        # Youpie
        Log(LOG_NOTICE, "Conversation instanciated correctly !")
        
    def test_removeConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        forum = self.plone.board.forum

        self.assertEqual(len(forum.contentValues('Conversation')), 0)
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        self.assertEqual(len(forum.contentValues('Conversation')), 1)

        self.failUnless(conv_id in forum.objectIds())

        forum.removeConversation(conv_id)
        self.assertEqual(len(forum.contentValues('Conversation')), 0)
     
        # Youpie
        Log(LOG_NOTICE, "Conversation removed correctly !")
        
    def test_addMessage(self):
        forum = self.plone.board.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        
        msg = conv.addMessage('msg_subject', 'msg_body')
        msg_id = msg.getId()
        self.assertEqual(msg.getSubject(), 'msg_subject')
        self.assertEqual(msg.getBody(), 'msg_body')
        # check if Message was cataloged
        self.failUnless(msg_id in [v.id for v in self.catalog(meta_type='Message', id=msg_id)])
        Log(LOG_NOTICE, "Conversation.addMessage() is OK!")
        
    def test_delOb(self):
        forum = self.plone.board.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        msg = conv.addMessage('msg_subject', 'msg_body')
        msg_id = msg.getId()
        
        self.assertEqual(conv.getNumberOfMessages(), 2)
        conv._delOb(msg_id)
        self.assertEqual(conv.getNumberOfMessages(), 1)
        Log(LOG_NOTICE, "Conversation._delOb() is OK!")
        
    def test_delObject(self):
        forum = self.plone.board.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        msg = conv.addMessage('msg_subject', 'msg_body')
        msg_id = msg.getId()
        
        self.assertEqual(conv.getNumberOfMessages(), 2)
        reply = msg.addReply('reply_subject', 'reply_body')
        # here we check that _delObject deletes all descendants of message
        self.assertEqual(conv.getNumberOfMessages(), 3)
        conv._delObject(msg_id)
        self.assertEqual(conv.getNumberOfMessages(), 1)
        self.assertEqual(conv.has_key(msg_id), 0)
        # check if Message was uncataloged
        self.failIf(msg_id in [v.id for v in self.catalog(meta_type='Message', id=msg_id)])
        Log(LOG_NOTICE, "Conversation._delObject() is OK!")
        
    def test_getMsgResponsesIds(self):
        forum = self.plone.board.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        msg = conv.addMessage('msg_subject', 'msg_body')
        msg_id = msg.getId()
        
        reply = msg.addReply('reply_subject', 'reply_body')
        reply_id = reply.getId()
        self.failUnless(reply_id in conv._getMsgResponsesIds(msg_id))
        reply1 = msg.addReply('reply1_subject', 'reply1_body')
        reply1_id = reply1.getId()
        self.failUnless(reply1_id in conv._getMsgResponsesIds(msg_id))
        Log(LOG_NOTICE, "Conversation._getMsgResponsesIds() is OK!")

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestConversation))
        return suite

