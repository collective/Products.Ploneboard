#
# Forum tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import PloneboardTestCase

class TestPloneboardForum(PloneboardTestCase.PloneboardTestCase):
    def testAddForum(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        self.loginPortalOwner()
        board = self.portal.board

        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        board.addForum('forum', 'title', 'description')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 1)

        self.failUnless('forum' in board.objectIds())

        self.assertEqual(board.forum.getId(), 'forum')
        self.assertEqual(board.forum.Title(), 'title')
        self.assertEqual(board.forum.Description(), 'description')
     
    def testRemoveForum(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        self.loginPortalOwner()
        board = self.portal.board

        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        board.addForum('forum', 'title', 'description')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 1)

        self.failUnless('forum' in board.objectIds())

        board.removeForum('forum')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        
    def test_delOb(self):
        self.loginPortalOwner()
        forum = self.portal.board.addForum('forum', 'title', 'description')
        conv = forum.addConversation('subject', 'body')
        conv1 = forum.addConversation('subject1', 'body1')
        self.assertEqual(forum.getNumberOfConversations(), 2)
        conv_id = conv1.getId()
        forum._delOb(conv_id)
        self.assertEqual(forum.getNumberOfConversations(), 1)
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboardForum))
        return suite
