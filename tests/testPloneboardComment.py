#
# Comment tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface.verify import verifyClass, verifyObject

import PloneboardTestCase, utils
from Products.Ploneboard.interfaces import IComment
from Products.Ploneboard.content.PloneboardComment import PloneboardComment

from OFS.Image import File
from Products.CMFPlone.utils import _createObjectByType


class TestPloneboardComment(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')

    def testInterfaceVerification(self):
        self.failUnless(verifyClass(IComment, PloneboardComment))
    
    def testGetConversation(self):
        comment = self.conv.objectValues()[0]
        self.failUnlessEqual(comment.getConversation(), self.conv)

    def testAddReply(self):
        conv = self.conv
        comment = conv.objectValues()[0]
        reply = comment.addReply('reply1', 'body1')
        self.failUnless(reply in conv.objectValues())
    
    def testInReplyTo(self):
        comment = self.conv.objectValues()[0]
        reply = comment.addReply('reply1', 'body1')
        self.failUnlessEqual(comment, reply.inReplyTo())

    def testGetReplies(self):
        comment = self.conv.objectValues()[0]
        reply = comment.addReply('reply1', 'body1')
        reply2 = comment.addReply('reply2', 'body2')
        self.failUnlessEqual(len(comment.getReplies()), 2)
        self.failUnless(reply in comment.getReplies())
        self.failUnless(reply2 in comment.getReplies())

    def testGetTitle(self):
        comment = self.conv.objectValues()[0]
        self.failUnlessEqual(comment.getTitle(), 'conv1')

    def testGetText(self):
        comment = self.conv.objectValues()[0]
        self.failUnlessEqual(comment.getText(), 'conv1 body')

    def testSetInReplyTo(self):
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        msg = conv.addComment('msg_subject', 'msg_body')
        msg1 = conv.addComment('msg_subject1', 'msg_body1')
        msg1.setInReplyTo(msg)
        self.assertEqual(msg.getId(), msg1.inReplyTo().getId())
       
    def testDeleteReply(self):
        conv = self.conv
     
        m = conv.objectValues()[0]
        self.assertEqual(conv.getNumberOfComments(), 1)
        r = m.addReply('reply1', 'body1')
        self.assertEqual(conv.getNumberOfComments(), 2)
        
        m.deleteReply(r)
        self.assertEqual(len(m.getReplies()), 0)

    def testMakeBranch(self):
        forum = self.forum
        conv = self.conv
        
        comment = conv.objectValues()[0]
        reply = comment.addReply('reply1', 'body1')
        reply1 = reply.addReply('reply2', 'body2')
        self.assertEqual(conv.getNumberOfComments(), 3)
        self.assertEqual(forum.getNumberOfConversations(), 1)
        
        branch = reply.makeBranch()
        
        self.assertEqual(conv.getNumberOfComments(), 1)
        self.assertEqual(forum.getNumberOfConversations(), 2)

        self.failIfEqual(branch, conv)
        self.assertEqual(branch.getNumberOfComments(), 2)

    def testChildIds(self):
        conv = self.conv
        msg = conv.objectValues()[0]
        r = msg.addReply('reply_subject', 'reply_body')
        r1 = msg.addReply('reply_subject1', 'reply_body1')
        r2 = msg.addReply('reply_subject2', 'reply_body2')
        r2.addReply('rs', 'rb').addReply('rs1', 'rb1').addReply('rs2', 'rb2')
        self.assertEqual(len(msg.childIds()), 6)
        
    def testTransforms(self):
        conv = self.conv
        msg = conv.objectValues()[0]
        text = 'Smiley :)'
        msg.setText(text)
        self.failUnless(msg.getText())
        self.failIfEqual(msg.getText(), text)
        self.failUnlessEqual(self.portal.portal_ploneboard.performCommentTransform(text), msg.getText())

class TestPloneboardCommentAttachmentSupport(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')

    def testAddAttachment(self):
        conv = self.conv
        msg = conv.objectValues()[0]
        
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        file = File('testfile', 'testtitle', 'asdf')
        msg.addAttachment(file=file, title='comment')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        self.failUnless(msg.getAttachment('testfile'))

    def testHasAttachment(self):
        pass

    def testRemoveAttachment(self):
        conv = self.conv
        msg = conv.objectValues()[0]
      
        file = File('testfile', 'testtitle', 'asdf')
        msg.addAttachment(file=file, title='comment')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        msg.removeAttachment('testfile')
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        
    def testGetAttachments(self):
        conv = self.conv
        msg = conv.objectValues()[0]
      
        file = File('testfile', 'testtitle', 'asdf')
        msg.addAttachment(file=file, title='comment')
        file1 = File('testfile1', 'testtitle1', 'asdf')
        msg.addAttachment(file=file1, title='comment1')
        self.assertEqual(len(msg.getAttachments()), 2)
        self.failUnless('comment' in [v.Title() for v in msg.getAttachments()])
        self.failUnless('comment1' in [v.Title() for v in msg.getAttachments()])


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboardComment))
        suite.addTest(unittest.makeSuite(TestPloneboardCommentAttachmentSupport))
        return suite
