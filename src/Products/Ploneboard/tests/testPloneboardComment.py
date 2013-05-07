#
# Comment tests
#

import unittest
from zope.interface.verify import verifyClass

import PloneboardTestCase
from Products.Ploneboard.interfaces import IComment
from Products.Ploneboard.content.PloneboardComment import PloneboardComment
from Products.Ploneboard.config import HAS_SIMPLEATTACHMENT

from OFS.Image import File
from Products.CMFPlone.utils import _createObjectByType

from Products.Ploneboard.tests.utils import addMember

class TestPloneboardComment(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')
        self.comment = self.conv.addComment("comment1", "comment1 body")

    def testInterfaceVerification(self):
        self.failUnless(verifyClass(IComment, PloneboardComment))

    def testGetConversation(self):
        self.failUnlessEqual(self.comment.getConversation(), self.conv)

    def testAddReply(self):
        conv = self.conv
        reply = self.comment.addReply('reply1', 'body1')
        self.failUnless(reply in conv.objectValues())

    def testAddReplyAsAnonymousTakesOwnerOfForumAndCreatorAnonymous(self):
        conv = self.conv
        self.logout()
        reply = self.comment.addReply('reply1', 'body1', creator='Anonymous')
        self.assertEqual(conv.getForum().owner_info()['id'], reply.owner_info()['id'])
        self.assertEqual(reply.Creator(), 'Anonymous')

    def testAddReplyAsNotAnonymousLeavesOwnershipAlone(self):
        conv = self.conv
        addMember(self, 'member2')
        self.login('member2')
        self.assertNotEqual(conv.getForum().owner_info()['id'], 'member2')
        reply = self.comment.addReply('reply1', 'body1')
        self.assertEqual(reply.owner_info()['id'], 'member2')

    def testAddReplyAddsRe(self):
        conv = self.conv
        reply = self.comment.addReply('', 'body1')
        self.assertEqual(reply.Title(), 'Re: ' + conv.Title())

    def testAddReplyAddsReOnlyOnce(self):
        conv = self.conv
        reply = self.comment.addReply('', 'body1')
        reply2 = reply.addReply('', 'body2')
        self.assertEqual(reply2.Title(), 'Re: ' + conv.Title())

    def testAddReplyOnlyAddsReIfNotSet(self):
        conv = self.conv
        reply = self.comment.addReply('reply1', 'body1')
        self.assertEqual(reply.Title(), 'reply1')

    def testInReplyTo(self):
        reply = self.comment.addReply('reply1', 'body1')
        self.failUnlessEqual(self.comment, reply.inReplyTo())

    def testGetReplies(self):
        reply = self.comment.addReply('reply1', 'body1')
        reply2 = self.comment.addReply('reply2', 'body2')
        self.failUnlessEqual(len(self.comment.getReplies()), 2)
        self.failUnless(reply in self.comment.getReplies())
        self.failUnless(reply2 in self.comment.getReplies())

    def testGetTitle(self):
        self.failUnlessEqual(self.comment.getTitle(), 'comment1')

    def testGetText(self):
        self.failUnlessEqual(self.comment.getText(), 'comment1 body')

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
        self.assertEqual(conv.getNumberOfComments(), 2)
        r = m.addReply('reply1', 'body1')
        self.assertEqual(conv.getNumberOfComments(), 3)

        m.deleteReply(r)
        self.assertEqual(len(m.getReplies()), 0)

    def testMakeBranch(self):
        forum = self.forum
        conv = self.conv

        comment = conv.objectValues()[0]
        reply = comment.addReply('reply1', 'body1')
        reply1 = reply.addReply('reply2', 'body2')
        self.assertEqual(conv.getNumberOfComments(), 4)
        self.assertEqual(forum.getNumberOfConversations(), 1)

        branch = reply.makeBranch()
        self.assertEqual(conv.getNumberOfComments(), 2)
        self.assertEqual(forum.getNumberOfConversations(), 2)

        self.failIfEqual(branch, conv)
        self.assertEqual(branch.getNumberOfComments(), 2)

    def testChildIds(self):
        conv = self.conv
        r = self.comment.addReply('reply_subject', 'reply_body')
        r1 = self.comment.addReply('reply_subject1', 'reply_body1')
        r2 = self.comment.addReply('reply_subject2', 'reply_body2')
        r2.addReply('rs', 'rb').addReply('rs1', 'rb1').addReply('rs2', 'rb2')
        self.assertEqual(len(self.comment.childIds()), 6)

    def testTransforms(self):
        conv = self.conv
        text = 'Smiley :)'
        self.comment.setText(text)
        self.failUnless(self.comment.getText())
        self.failIfEqual(self.comment.getText(), text)
        self.failUnlessEqual(self.portal.portal_ploneboard.performCommentTransform(text), self.comment.getText())

    def XXXtestDeleting(self):
        pass

    def testNewCommentIsVisibleToAnonymous(self):
        comment = self.conv.addComment('subject2', 'body2')
        id = comment.getId()
        self.logout()
        comments = self.conv.getComments()
        self.failUnless(id in [x.getId() for x in comments])
    
    def testMemberWithNoFullname(self):
        addMember(self, 'membernofullname', fullname='')
        self.login('membernofullname')
        comment = self.conv.addComment('subject3', 'body3')
        commentview = comment.restrictedTraverse('@@singlecomment_view')
        self.assertEqual(commentview.author(), 'membernofullname')

    def testMemberWithFullname(self):
        addMember(self, 'memberwithfullname', fullname='MemberName')
        self.login('memberwithfullname')
        comment = self.conv.addComment('subject4', 'body4')
        commentview = comment.restrictedTraverse('@@singlecomment_view')
        self.assertEqual(commentview.author(), 'MemberName')




class TestPloneboardCommentAttachmentSupport(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')
        self.comment = self.conv.addComment("comment1", "comment1 body")

    def testAddAttachment(self):
        conv = self.conv

        self.assertEqual(self.comment.getNumberOfAttachments(), 0)
        file = File('testfile', 'testtitle', 'asdf')
        self.comment.addAttachment(file=file, title='comment')
        self.assertEqual(self.comment.getNumberOfAttachments(), 1)
        self.failUnless(self.comment.getAttachment('testfile'))

    def testHasAttachment(self):
        pass

    def testRemoveAttachment(self):
        conv = self.conv

        file = File('testfile', 'testtitle', 'asdf')
        self.comment.addAttachment(file=file, title='comment')
        self.assertEqual(self.comment.getNumberOfAttachments(), 1)
        self.comment.removeAttachment('testfile')
        self.assertEqual(self.comment.getNumberOfAttachments(), 0)


    def testAttachmentRestrictionChanging(self):
        conv = self.conv
        self.forum.setMaxAttachments(10)
        self.failUnlessEqual(self.comment.getNumberOfAllowedAttachments(), 10)
        self.forum.setMaxAttachments(1)
        self.failUnlessEqual(self.comment.getNumberOfAllowedAttachments(), 1)


    def tryAttachmentSizeRestrictions(self, msg):
        self.forum.setMaxAttachments(10)

        self.forum.setMaxAttachmentSize(1)
        file = File('testfile', 'testtitle', 'X')
        msg.addAttachment(file=file, title='comment')
        msg.removeAttachment('testfile')

        file = File('testfile', 'testtitle', 'X'*2048)
        try:
            msg.addAttachment(file=file, title='comment')
        except ValueError:
            pass
        else:
            self.fail("Can add too many attachments")

        self.forum.setMaxAttachmentSize(2)
        msg.addAttachment(file=file, title='comment')


    def testAttachmentSizeRestriction(self):
        conv = self.conv
        self.tryAttachmentSizeRestrictions(self.comment)

    def testAttachmentSizeRestrictionsOnChild(self):
        conv = self.conv
        reply = self.comment.addReply('reply1', 'body1')
        self.tryAttachmentSizeRestrictions(reply)


    def testAttachmentNumberRestriction(self):
        conv = self.conv
        self.forum.setMaxAttachments(1)
        file = File('testfile', 'testtitle', 'asdf')
        self.comment.addAttachment(file=file, title='comment')
        file = File('testfile2', 'testtitle2', 'asdf')
        try:
            self.comment.addAttachment(file=file, title='another comment')
        except ValueError:
            pass
        else:
            self.fail("Can add too many attachments")


    def testGetAttachments(self):
        conv = self.conv
        self.forum.setMaxAttachments(5)

        file = File('testfile', 'testtitle', 'asdf')
        self.comment.addAttachment(file=file, title='comment')
        file1 = File('testfile1', 'testtitle1', 'asdf')
        self.comment.addAttachment(file=file1, title='comment1')
        self.assertEqual(len(self.comment.getAttachments()), 2)
        self.failUnless('comment' in [v.Title() for v in self.comment.getAttachments()])
        self.failUnless('comment1' in [v.Title() for v in self.comment.getAttachments()])

    def testDeleteing(self):
        """Test deleting a comment.
        """

        # Was going to use doctests for this until I realized that
        # PloneTestCase has no doctest capability :(
        # - Rocky

        # Actually - it does!
        # see http://plone.org/documentation/tutorial/testing :)
        # - Martin

        # Now lets start adding some comments:
        first_comment = self.conv.getFirstComment()
        c1 = first_comment.addReply('foo1', 'bar1')
        c2 = first_comment.addReply('foo2', 'bar2')
        c21 = c2.addReply('foo3', 'bar3')

        # Make sure the first comment has exactly two replies:

        self.assert_(first_comment.getReplies(), [c1, c2])

        # Now lets try deleting the first reply to the main comment:

        c1.delete()
        self.assert_(first_comment.getReplies(), [c2])

        # Ok, so lets try deleting a comment that has replies to it:

        c2.delete()

        # Now even though we deleted the last remaining reply to
        # first_comment, we should still have another reply because
        # deleting a reply that had a child will make that child seem
        # as though it is a reply to its parent's parent.

        self.assert_(first_comment.getReplies(), [c21])

        # lets add a comment to c21

        c211 = c21.addReply('foo4', 'bar4')

        # Once the only root comment is deleted that means the conversation's
        # sole root comment should become c211

        c21.delete()
        self.assert_(self.conv.getRootComments(), [c211])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneboardComment))
    if HAS_SIMPLEATTACHMENT:
        suite.addTest(unittest.makeSuite(TestPloneboardCommentAttachmentSupport))

    return suite
