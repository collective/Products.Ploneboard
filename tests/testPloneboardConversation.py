#
# Conversation tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import PloneboardTestCase, utils

from Products.CMFPlone.utils import _createObjectByType


class TestPloneboardConversation(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self._refreshSkinData()
        utils.disableScriptValidators(self.portal)

        _createObjectByType('Ploneboard', self.portal, 'board')
        _createObjectByType('PloneboardForum', self.portal.board, 'forum')
        self.catalog = self.portal.board.getInternalCatalog()

    def testAddConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        forum = self.portal.board.forum

        self.assertEqual(len(forum.contentValues('PloneboardConversation')), 0)
        conv = forum.addConversation('subject', 'body', script=0)
        conv_id = conv.getId()
        self.assertEqual(len(forum.contentValues('PloneboardConversation')), 1)

        self.failUnless(conv_id in forum.objectIds())

        self.assertEqual(conv.Title(), 'subject')
        self.failUnless(conv_id in [v.getId for v in self.catalog(meta_type='PloneboardConversation', id=conv_id)])
     
    def testRemoveConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        forum = self.portal.board.forum

        self.assertEqual(len(forum.contentValues('PloneboardConversation')), 0)
        conv = forum.addConversation('subject', 'body', script=0)
        conv_id = conv.getId()
        self.assertEqual(len(forum.contentValues('PloneboardConversation')), 1)

        self.failUnless(conv_id in forum.objectIds())

        forum.removeConversation(conv_id)
        self.assertEqual(len(forum.contentValues('PloneboardConversation')), 0)
        self.failIf(conv_id in [v.id for v in self.catalog(meta_type='PloneboardConversation', id=conv_id)])
     
    def testAddComment(self):
        forum = self.portal.board.forum
        conv = forum.addConversation('subject', 'body', script=0)
        conv_id = conv.getId()
        
        msg = conv.addComment('msg_subject', 'msg_body')
        msg_id = msg.getId()
        self.assertEqual(msg.getSubject(), 'msg_subject')
        self.assertEqual(msg.getBody(), 'msg_body')
        # check if Comment was cataloged
        self.failUnless(msg_id in [v.getId for v in self.catalog(meta_type='PloneboardComment', id=msg_id)])
        
    def test_delOb(self):
        forum = self.portal.board.forum
        conv = forum.addConversation('subject', 'body', script=0)
        self.assertEqual(len(conv.objectIds()), 1) # Fails, wtf?
        msg = conv.addComment('msg_subject', 'msg_body')
        msg_id = msg.getId()
        self.failUnless(msg_id in list(conv.objectIds()))
        conv._delOb(msg_id)
        self.failIf(msg_id in list(conv.objectIds()))

    def test_delObject(self):
        forum = self.portal.board.forum
        conv = forum.addConversation('subject', 'body', script=1)
        msg = conv.addComment('msg_subject', 'msg_body')
        #msg = conv.objectValues()[0]
        r = msg.addReply('reply_subject', 'reply_body')
        r1 = msg.addReply('reply_subject1', 'reply_body1')
        r2 = msg.addReply('reply_subject2', 'reply_body2')
        r2.addReply('rs', 'rb').addReply('rs1', 'rb1').addReply('rs2', 'rb2')
        self.failUnless(r.getId() in [v.getId for v in self.catalog(meta_type='PloneboardComment', id=r.getId())])
        self.assertEqual(conv.getNumberOfComments(), 7)
        conv._delObject(r2.getId(), recursive=1)
        self.assertEqual(conv.getNumberOfComments(), 3)
        # check if we delete conversation so we delete root comment
        self.assertEqual(forum.getNumberOfConversations(), 1)
        conv._delObject(msg.getId(), recursive=1)
        self.assertEqual(forum.getNumberOfConversations(), 0)
        # check if Comment was uncataloged
        self.failIf(r.getId() in [v.id for v in self.catalog(meta_type='PloneboardComment', id=r.getId())])
        self.failIf(msg.getId() in [v.id for v in self.catalog(meta_type='PloneboardComment', id=msg.getId())])
        
        # Checking non recursive delete
        conv = forum.addConversation('subject', 'body', script=0)
        msg = conv.objectValues()[0]
        r = msg.addReply('reply_subject', 'reply_body')
        self.assertEqual(conv.getNumberOfComments(), 2)
        self.failUnless(r.getId() in [v.getId for v in self.catalog(meta_type='PloneboardComment', id=r.getId())])
        conv._delObject(msg.getId())
        self.assertEqual(conv.getNumberOfComments(), 1)
        self.failUnless(r.getId() in [v.getId for v in self.catalog(meta_type='PloneboardComment', id=r.getId())])
        
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboardConversation))
        return suite