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
        get_transaction().commit(1)

if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestRegistration))
        return suite
