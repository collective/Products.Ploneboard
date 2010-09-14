#
# Comment tests
#

import unittest
from Products.Ploneboard.tests import PloneboardTestCase
from Products.CMFPlone.utils import _createObjectByType

class TestITextContentAdapter(PloneboardTestCase.PloneboardTestCase):

    def afterSetUp(self):
        from Products.ATContentTypes.interface import ITextContent 
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')
        self.comment = self.conv.addComment("c1 title", "c1 body")
        self.textContent = ITextContent(self.comment)
        

    def testGetText(self):
        self.assertEqual(self.comment.getText(), 
                         self.textContent.getText())
    
    def testSetText(self):
        s = 'blah'
        self.textContent.setText('blah')
        
        self.assertEqual(self.comment.getText(), s)
        self.assertEqual(self.textContent.getText(), s)
        
    def testCookedBody(self):
        self.assertEqual(self.textContent.CookedBody(), 
                         self.comment.getText())

    def testEditableBody(self):
        self.assertEqual(self.textContent.CookedBody(), 
                         self.comment.getRawText())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestITextContentAdapter))
    return suite
