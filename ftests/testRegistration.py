#
# Skeleton functional test with mechanize
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFMember.tests import CMFMemberTestCase

from Acquisition import aq_base
from Products.CMFPlone.Portal import default_frontpage

from mechanize import Browser
from urllib import urlencode
from urlparse import urlparse
import pullparser
import re

ZopeTestCase.utils.startZServer()

default_user = PloneTestCase.default_user

_d = {'__ac_name': default_user,
      '__ac_password': 'secret'}


class TestRegistration(ZopeTestCase.Functional, CMFMemberTestCase.CMFMemberTestCase):

    def afterSetUp(self):
        # Fire up mech browser
        self.portal_url = self.portal.absolute_url()
        self.folder_url = self.folder.absolute_url()
        CMFMemberTestCase.CMFMemberTestCase.afterSetUp(self)
        self.b = Browser()

    def testRegistration(self):
        self.b.open(self.portal_url+'/createMember')

        self.b.select_form('edit_form')
        self.b['id'] = 'test1'
        self.b['fullname'] = 'test1'
        self.b['email'] = 'test@example.com'
        self.b['password'] = 'secret'
        self.b['confirm_password'] = 'secret'
        #self.b['mail_me_visible'] = 0
        destination = self.b.open(self.b.click())
        p = pullparser.PullParser(destination)
        msg = self.getTheTag(p, "div", **{'class':'portalMessage'})
        # XXX this is not i18n smart, how do we handle this?
        self.failUnless("You have been registered" in msg)
        #get_transaction().commit(1)

    def tryToGetThePassword(self, userId):
        self.b.open(self.portal_url+'/mail_password_form')
        self.b.select_form('mail_password')
        self.b['userid'] = userId
        destination = self.b.open(self.b.click())

        # If not authorized we'll end up on the login_form
        url = self.b.geturl()
        return 'login_form' not in url and 'mail_password' in url
        
    def testMailForgottenPasswordApprovalUser(self):
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(('Member',), 'member_approval_workflow')
        wf_tool.updateRoleMappings()
        member = self.membership.getMemberById( self.portal_user_info['id'])
        member.setEmail('nobody@neverexistingdomain.fake')
        # Verify that we start in public state 
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'public')
        self.failUnless( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        
        # Going to disable
        wf_tool.doActionFor( member, 'disable' )
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'disabled')
        self.failIf( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        
        # and to private 
        # you can only enable the member back to old state, should it be like that?
        wf_tool.doActionFor( member, 'enable_public' )
        wf_tool.doActionFor( member, 'make_private' )
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'private')
        self.failUnless( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        
    def testMailForgottenPasswordAutoUser(self):
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(('Member',), 'member_auto_workflow')
        wf_tool.updateRoleMappings()
        member = self.membership.getMemberById( self.portal_user_info['id'])
        member.setEmail('nobody@neverexistingdomain.fake')
        # Verify that we start in public state 
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'public')
        self.failUnless( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        
        # Going to disable
        wf_tool.doActionFor( member, 'disable' )
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'disabled')
        self.failIf( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        
        # and to private 
        # you can only enable the member back to old state, should it be like that?
        wf_tool.doActionFor( member, 'enable_public' )
        wf_tool.doActionFor( member, 'make_private' )
        self.failUnless(wf_tool.getInfoFor(member, 'review_state') == 'private')
        self.failUnless( self.tryToGetThePassword( self.portal_user_info['id'] ) )
        

if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestRegistration))
        return suite
