#
# Forum tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import PloneboardTestCase, utils

from Products.CMFPlone.utils import _createObjectByType


class TestPloneboardForum(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        self._refreshSkinData()
        utils.disableScriptValidators(self.portal)

        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.catalog = self.board.getInternalCatalog()

    def testAddForum(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        board = self.board

        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        board.addForum('forum', 'title', 'description')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 1)

        self.failUnless('forum' in board.objectIds())

        self.assertEqual(board.forum.getId(), 'forum')
        self.assertEqual(board.forum.Title(), 'title')
        self.assertEqual(board.forum.Description(), 'description')
        self.assertEqual(board.forum.Description(mimetype='text/html'), '<p>description</p>')
     
    def testRemoveForum(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        board = self.board

        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        board.addForum('forum', 'title', 'description')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 1)

        self.failUnless('forum' in board.objectIds())

        board.removeForum('forum')
        self.assertEqual(len(board.contentValues('PloneboardForum')), 0)
        
    def test_delOb(self):
        forum = self.board.addForum('forum', 'title', 'description')
        self.assertEqual(forum.getNumberOfConversations(), 0)
        conv = forum.addConversation('subject', 'body', script=0)
        self.failUnless(conv.getId() in list(forum.objectIds()))
        conv1 = forum.addConversation('subject1', 'body1', script=0)
        self.failUnless(conv1.getId() in list(forum.objectIds()))
        conv_id = conv1.getId()
        forum._delOb(conv_id)
        self.failIf(conv1.getId() in list(forum.objectIds()))

        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboardForum))
        return suite
