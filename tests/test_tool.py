# OxfamAmerica.
# Copyright (C) 2004 Enfold Systems, LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(os.path.dirname(sys.argv[0]), 'framework.py'))

# Load fixture
from Testing import ZopeTestCase
from base import BaseTest
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

class SquidPathTest(BaseTest):

    def afterSetUp(self):
        BaseTest.afterSetUp(self)
        self.loginPortalOwner()
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.qi.installProduct('CMFSquidTool')
        self.make_structure()

    def make_structure(self):
        portal = self. portal
        portal.invokeFactory('Folder', id='public_website')
        portal.public_website.invokeFactory('Folder', id='en')
        portal.public_website.en.invokeFactory('Document', id='index_html')

    def test_rewriteurl(self):
        from Products.CMFSquidTool.SquidTool import URL_REWRITE_MAP
        original='http://nohost/portal/public_website/en'
        modified='http://oxfamamerica.org'
        URL_REWRITE_MAP[original]=modified

        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        ut = getToolByName(portal, 'portal_url')
        content = portal.public_website.en.index_html
        url = content.absolute_url() 
        self.failUnless(st.rewriteUrl(url) == modified+'/index_html')

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    for testClass in (
        SquidPathTest,
                      ):
        suite.addTest(unittest.makeSuite(testClass))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
