#
# Event notification tests
#


import unittest
import zope.component
from Products.Ploneboard.tests import PloneboardTestCase
from Products.Archetypes.event import ObjectInitializedEvent

from Products.CMFPlone.utils import _createObjectByType


notified = []

@zope.component.adapter(ObjectInitializedEvent)
def dummyEventHandler(event):
    notified.append(event.object)


class TestPloneboardEventNotifications(PloneboardTestCase.PloneboardTestCase):
    """Test the events that should be fired when conversations or comments are added"""

    def afterSetUp(self):
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        zope.component.provideHandler(dummyEventHandler)

    def testPloneboardEventNotifications(self):
        conv = self.forum.addConversation('subject', 'body')
        self.failUnless(conv in notified)
        comment = conv.addComment('subject', 'body')
        self.failUnless(comment in notified)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneboardEventNotifications))
    return suite
