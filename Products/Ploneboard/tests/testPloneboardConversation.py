#
# Conversation tests
#

import transaction
import unittest
from zope.interface.verify import verifyClass, verifyObject
import PloneboardTestCase

from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.interfaces import IConversation
from Products.Ploneboard.content.PloneboardConversation import PloneboardConversation

from Products.Ploneboard.tests.utils import addMember

class TestPloneboardConversation(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('subject', 'body')
        self.comment = self.conv.getComments()[0]

    def testInterfaceVerification(self):
        self.failUnless(verifyClass(IConversation, PloneboardConversation))

    def testInterfaceConformance(self):
        self.failUnless(IConversation.providedBy(self.conv))
        self.failUnless(verifyObject(IConversation, self.conv))

    def testGetForum(self):
        self.failUnlessEqual(self.forum, self.conv.getForum())

    def testAddComment(self):
        msg = self.conv.addComment('msg_title', 'msg_text')
        self.assertEqual(msg.getTitle(), 'msg_title')
        self.assertEqual(msg.getText(), 'msg_text')

    def testGetLastComment(self):
        msg = self.conv.addComment('last_comment_title', 'last_comment_text')
        self.assertEqual(self.conv.getLastComment().getTitle(), msg.getTitle())
        msg2 = self.conv.addComment('last_comment_title2', 'last_comment_text')
        self.assertEqual(self.conv.getLastComment().getTitle(), msg2.getTitle())

    def testGetComment(self):
        conv = self.conv
        self.failUnlessEqual(self.comment, conv.getComment(self.comment.getId()))

    def testGetComments(self):
        conv = self.conv
        comment2 = conv.addComment('subject2', 'body2')
        self.failUnlessEqual(conv.getComments(), [self.comment, comment2]) 

    def testGetCommentsSlicing(self):
        conv = self.conv
        comment2 = conv.addComment('subject2', 'body2')
        self.failUnlessEqual(conv.getComments(limit=1, offset=0), [self.comment]) 
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
        self.failUnlessEqual(self.comment.created(), conv.getLastCommentDate())
        comment = conv.addComment('followup', 'text')
        self.failUnlessEqual(comment.created(), conv.getLastCommentDate())

    def testGetRootComments(self):
        conv = self.conv
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 1)

        conv.addComment("base2", "base two")
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 2)

        reply = self.comment.addReply('anotherfollowup', 'moretext')
        threaded = conv.getRootComments()
        self.failUnlessEqual(len(threaded), 2)
        self.failUnlessEqual(len(self.comment.getReplies()), 1)

    def testGetFirstComment(self):
        conv = self.conv
        first = conv.getFirstComment()
        self.failUnless(first)
        self.failUnlessEqual(first, conv.objectValues()[0])
        conv.addComment('followup', 'text')
        self.failUnlessEqual(first, conv.getFirstComment())

    def testModificationDate(self):
        conv = self.conv
        modified1 = conv.modified()
        from time import sleep
        sleep(0.1) # To make sure modified is different
        conv.addComment('followup', 'text')
        modified2 = conv.modified()
        self.failIfEqual(modified1, modified2)
        conv.objectValues()[0].addReply('followup', 'text')
        sleep(0.1) # To make sure modified is different
        modified3 = conv.modified()
        self.failIfEqual(modified1, modified3)
        self.failIfEqual(modified2, modified3)

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
        
    def testNewConversationIsVisibleToAnonymous(self):
        conv = self.forum.addConversation('subject2', 'body2')
        conv.addComment("comment", "comment")
        id = conv.getId()
        self.logout()
        convs = self.forum.getConversations()
#        self.failUnless(id in [x.getId() for x in convs])
        comments = conv.getComments()
        self.assertEqual(len(comments), 2)
        
    def testAddCommentAsAnonymousTakesOwnerOfForumAndCreatorAnonymous(self):
        conv = self.conv
        self.logout()
        reply = conv.addComment('reply1', 'body1', creator='Anonymous')
        self.assertEqual(conv.getForum().owner_info()['id'], reply.owner_info()['id'])
        self.assertEqual(reply.Creator(), 'Anonymous')
    
    def testAddCommentAsNotAnonymousLeavesOwnershipAlone(self):
        conv = self.conv
        addMember(self, 'member2')
        self.login('member2')
        self.assertNotEqual(conv.getForum().owner_info()['id'], 'member2')
        reply = conv.addComment('reply1', 'body1')
        self.assertEqual(reply.owner_info()['id'], 'member2')

    def testDuplicateConversations(self):
        conv2 = self.forum.addConversation('subject2', 'body2')
        comment = conv2.addComment('subject2', 'body2')
        transaction.savepoint(optimistic=True)
        cp = self.forum.manage_copyObjects(conv2.getId())
        self.failUnlessRaises(ValueError, self.conv.manage_pasteObjects, cp)

    def testMergeConversations(self):
        conv2 = self.forum.addConversation('subject2', 'body2')
        comment = conv2.getComments()[0]
        transaction.savepoint(optimistic=True)
        self.conv.manage_pasteObjects(self.forum.manage_cutObjects(conv2.getId()))
        self.failUnless(comment.getId() in self.conv.objectIds())
        self.failUnless(len(self.conv.getComments()) == 2)
        self.failIf(conv2.getId() in self.forum.objectIds())

    def testMoveCommentToConversation(self):
        conv2 = self.forum.addConversation('subject2', 'body2')
        comment = conv2.addComment('subject2', 'body2')
        transaction.savepoint(optimistic=True)
        self.conv.manage_pasteObjects(conv2.manage_cutObjects(comment.getId()))
        self.failUnless(comment.getId() in self.conv.objectIds())
        self.failUnless(len(self.conv.getComments()) == 2)
        self.failUnless(conv2.getId() in self.forum.objectIds()) # We only moved the comment


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneboardConversation))
    return suite
