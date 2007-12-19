#
# Forum tests
#

import unittest
from zope.interface.verify import verifyClass, verifyObject

import PloneboardTestCase
from Products.Ploneboard.interfaces import IForum
from Products.Ploneboard.content.PloneboardForum import PloneboardForum

from Products.CMFPlone.utils import _createObjectByType


class TestPloneboardForum(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')

    def testInterfaceVerification(self):
        self.failUnless(verifyClass(IForum, PloneboardForum))

    def testInterfaceConformance(self):
        self.failUnless(IForum.providedBy(self.forum))
        self.failUnless(verifyObject(IForum, self.forum))        

    def testForumFields(self):
        """
        Check the fields on Forum, especially the Description field mimetypes.
        """
        forum = self.forum
        self.assertEqual(forum.getId(), 'forum')
        forum.setTitle('title')
        self.assertEqual(forum.Title(), 'title')
        forum.setDescription('description')
        self.assertEqual(forum.Description(), 'description')
        self.assertEqual(forum.Description(mimetype='text/html'), '<p>description</p>')

    def testForumCategory(self):
        self.failUnlessEqual(len(self.forum.getCategories()), 0)
        self.board.setCategories(['Category'])
        self.failUnlessEqual(len(self.forum.getCategories()), 1)

    # Interface tests

    def testGetBoard(self):
        self.failUnlessEqual(self.board, self.forum.getBoard())

    def testGetBoardOutsideStrictContainment(self):
        forum = _createObjectByType('PloneboardForum', self.folder, 'forum')
        self.failUnlessEqual(None, forum.getBoard())

    def testAddConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        self.failUnless(conv_id in forum.objectIds())
        self.assertEqual(conv.Title(), 'subject')

    def testGetConversation(self):
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        self.failUnlessEqual(conv, forum.getConversation(conv.getId()))

    def testGetConversationOutsideStrictContainment(self):
        # Make a folder inside the forum, then a conversation in the folder
        pass

    def testRemoveConversation(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        conv_id = conv.getId()
        forum.removeConversation(conv_id)
        self.assertEqual(len(forum.objectIds()), 0)
        self.failIf(conv_id in forum.objectIds())

    def testGetConversations(self):
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        conv2 = forum.addConversation('subject2', 'body2')
        # Notice reverse ordering, last always first
        self.failUnlessEqual(forum.getConversations(), [conv2, conv]) 
        # Check to make sure it doesn't get comments elsewhere
        forum2 = _createObjectByType('PloneboardForum', self.board, 'forum2')
        forum2.addConversation('subject', 'body')
        self.failUnlessEqual(forum.getConversations(), [conv2, conv]) 

    def testGetConversationsWithSlicing(self):
        forum = self.forum
        conv = forum.addConversation('subject', 'body')
        conv2 = forum.addConversation('subject2', 'body2')
        self.failUnlessEqual(forum.getConversations(limit=1, offset=0), [conv2]) 
        self.failUnlessEqual(forum.getConversations(limit=1, offset=1), [conv]) 

    def testGetConversationsOutsideStrictContainment(self):
        # Make a folder inside the forum, then a conversation in the folder
        pass

    def testGetNumberOfConversations(self):
        forum = self.forum
        self.failUnlessEqual(forum.getNumberOfConversations(), 0)
        conv = forum.addConversation('subject', 'body')
        self.failUnlessEqual(forum.getNumberOfConversations(), 1)
        conv2 = forum.addConversation('subject2', 'body2')
        self.failUnlessEqual(forum.getNumberOfConversations(), 2)
        forum.removeConversation(conv.getId())
        self.failUnlessEqual(forum.getNumberOfConversations(), 1)
        # Check to make sure it doesn't count conversations elsewhere
        forum2 = _createObjectByType('PloneboardForum', self.board, 'forum2')
        conv = forum2.addConversation('subject', 'body')
        self.failUnlessEqual(forum.getNumberOfConversations(), 1)

    def testGetNumberOfComments(self):
        forum = self.forum
        self.failUnlessEqual(forum.getNumberOfComments(), 0)
        conv = forum.addConversation('subject', 'body')
        self.failUnlessEqual(forum.getNumberOfComments(), 0)
        conv2 = forum.addConversation('subject2', 'body2')
        self.failUnlessEqual(forum.getNumberOfComments(), 0)
        forum.removeConversation(conv.getId())
        self.failUnlessEqual(forum.getNumberOfComments(), 0)
        conv2.addComment('followup', 'text')
        self.failUnlessEqual(forum.getNumberOfComments(), 1)
        # Check to make sure it doesn't count comments elsewhere
        forum2 = _createObjectByType('PloneboardForum', self.board, 'forum2')
        conv = forum2.addConversation('subject', 'body')
        conv.addComment("another", "another")
        self.failUnlessEqual(forum.getNumberOfComments(), 1)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneboardForum))
    return suite
