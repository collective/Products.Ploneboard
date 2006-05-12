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
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('subject', 'body')

    def testGetForum(self):
        self.failUnlessEqual(self.forum, self.conv.getForum())

    def testAddComment(self):
        msg = self.conv.addComment('msg_title', 'msg_text')
        self.assertEqual(msg.getTitle(), 'msg_title')
        self.assertEqual(msg.getText(), 'msg_text')

    def testGetComment(self):
        conv = self.conv
        comment = conv.addComment('subject', 'body')
        self.failUnlessEqual(comment, conv.getComment(comment.getId()))

    def testGetComments(self):
        conv = self.conv
        comment = conv.objectValues()[0]
        comment2 = conv.addComment('subject2', 'body2')
        self.failUnlessEqual(conv.getComments(), [comment, comment2]) 

    def testGetCommentsSlicing(self):
        conv = self.conv
        comment = conv.objectValues()[0]
        comment2 = conv.addComment('subject2', 'body2')
        self.failUnlessEqual(conv.getComments(limit=1, offset=0), [comment]) 
        self.failUnlessEqual(conv.getComments(limit=1, offset=1), [comment2]) 

    def testGetNumberOfComments(self):
        conv = self.conv
        self.failUnlessEqual(conv.getNumberOfComments(), 1)
        conv.addComment('followup', 'text')
        self.failUnlessEqual(conv.getNumberOfComments(), 2)
        # Check to make sure it doesn't count comments elsewhere
        conv2 = self.forum.addConversation('subject', 'body')
        self.failUnlessEqual(conv.getNumberOfComments(), 2)

    def testGetLastCommentDate(self):
        conv = self.conv
        comment = conv.objectValues()[0]
        self.failUnlessEqual(comment.created(), conv.getLastCommentDate())
        comment = conv.addComment('followup', 'text')
        self.failUnlessEqual(comment.created(), conv.getLastCommentDate())

    def testGetRootComments(self):
        conv = self.conv
        comment = conv.objectValues()[0]
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 1)

        comment = conv.addComment('followup', 'text')
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 2)

        reply = comment.addReply('anotherfollowup', 'moretext')
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 2)
        self.failUnlessEqual(len(comment.getReplies()), 1)

    def testGetFirstComment(self):
        conv = self.conv
        first = conv.getFirstComment()
        self.failUnless(first)
        conv.addComment('followup', 'text')
        self.failUnlessEqual(first, conv.getFirstComment())
        
    def XXXtest_delObject(self):
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        msg = conv.addComment('msg_title', 'msg_text')
        #msg = conv.objectValues()[0]
        r = msg.addReply('reply_subject', 'reply_body')
        r1 = msg.addReply('reply_subject1', 'reply_body1')
        r2 = msg.addReply('reply_subject2', 'reply_body2')
        r2.addReply('rs', 'rb').addReply('rs1', 'rb1').addReply('rs2', 'rb2')
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
        conv = forum.addConversation('subject', 'body')
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
