#
# Message tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import PloneboardTestCase

class TestPloneboardMessage(PloneboardTestCase.PloneboardTestCase):
    def testSetInReplyTo(self):
        self.loginPortalOwner()
        forum = self.portal.board.forum
        conv = forum.addConversation('subject', 'body')
        msg = conv.addMessage('msg_subject', 'msg_body')
        msg1 = conv.addMessage('msg_subject1', 'msg_body1')
        msg1.setInReplyTo(msg)
        self.assertEqual(msg.getId(), msg1.inReplyTo().getId())
       
    def testAddReply(self):
        self.loginPortalOwner()
        conv = self.conv
     
        m = conv.objectValues()[0]
        self.assertEqual(conv.getNumberOfMessages(), 1)
        r = m.addReply('reply1', 'body1')
        self.assertEqual(conv.getNumberOfMessages(), 2)
        # check that inReplyTo of added reply is equal to Message.id, it is in reply to
        self.assertEqual(m.getId(), r.inReplyTo().getId())
        
        self.assertEqual(len(m.getReplies()), 1)
        
        self.assertEqual(m.getReplies()[0].getId(), r.getId())
    
    def testDeleteReply(self):
        self.loginPortalOwner()
        conv = self.conv
     
        m = conv.objectValues()[0]
        self.assertEqual(conv.getNumberOfMessages(), 1)
        r = m.addReply('reply1', 'body1')
        self.assertEqual(conv.getNumberOfMessages(), 2)
        
        m.deleteReply(r.getId())
        self.assertEqual(len(m.getReplies()), 0)
        

    def testMakeBranch(self):
        self.loginPortalOwner()
        forum = self.portal.board.forum
        conv = self.conv
        
        m = conv.objectValues()[0]
        r = m.addReply('reply1', 'body1')
        r1 = r.addReply('reply2', 'body2')
        self.assertEqual(conv.getNumberOfMessages(), 3)
        self.assertEqual(forum.getNumberOfConversations(), 1)
        
        r.makeBranch()
        
        self.assertEqual(conv.getNumberOfMessages(), 1)
        self.assertEqual(forum.getNumberOfConversations(), 2)
        conv2 = forum.getConversation('2')
        self.failIfEqual(conv2.getId(), conv.getId())
        self.assertEqual(conv2.getNumberOfMessages(), 2)
        
    def testAddAttachment(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
        
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        msg.addAttachment(title='message', file='./PloneboardMessage.py')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        self.assertEqual(msg.getAttachment(0).title, 'message')
        
    def testRemoveAttachment(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
      
        msg.addAttachment(title='message', file='./PloneboardMessage.py')
        self.assertEqual(msg.getNumberOfAttachments(), 1)
        msg.removeAttachment(index=0)
        self.assertEqual(msg.getNumberOfAttachments(), 0)
        
    def testChangeAttachment(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
      
        msg.addAttachment(title='message', file='./PloneboardMessage.py')
        self.assertEqual(msg.getAttachment(index=0).title, 'message')
        old_data = str(msg.getAttachment(index=0))
        msg.changeAttachment(index=0, title='conv', file='./PloneboardConversation.py')
        self.assertEqual(msg.getAttachment(index=0).title, 'conv')
        self.assertNotEqual(str(msg.getAttachment(index=0)), old_data)
        
    def testGetAttachments(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
      
        msg.addAttachment(title='message', file='./PloneboardMessage.py')
        msg.addAttachment(title='message1', file='./PloneboardConversation.py')
        self.assertEqual(len(msg.getAttachments()), 2)
        self.failUnless('message' in [v.title for v in msg.getAttachments()])
        self.failUnless('message1' in [v.title for v in msg.getAttachments()])
    
    def testChildIds(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
        r = msg.addReply('reply_subject', 'reply_body')
        r1 = msg.addReply('reply_subject1', 'reply_body1')
        r2 = msg.addReply('reply_subject2', 'reply_body2')
        r2.addReply('rs', 'rb').addReply('rs1', 'rb1').addReply('rs2', 'rb2')
        self.assertEqual(len(msg.childIds()), 6)
        
    def testGetReplies(self):
        self.loginPortalOwner()
        conv = self.conv
        msg = conv.objectValues()[0]
        r = msg.addReply('r1', 'b1')
        r2 = msg.addReply('r2', 'b2')
        self.assertEqual(len(msg.getReplies()), 2)
        self.failUnless(r.getId() in map(lambda x: x.getId(), msg.getReplies()))
        self.failUnless(r2.getId() in map(lambda x: x.getId(), msg.getReplies()))
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboardMessage))
        return suite
