#
# Ploneboard tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.Ploneboard.tests import PloneboardTestCase
from Products.Ploneboard.interfaces import IPloneboard, IForum, IConversation, IComment

# Catch errors in Install
from Products.Ploneboard.Extensions import Install

from Products.CMFPlone.utils import _createObjectByType


class TestSetup(PloneboardTestCase.PloneboardTestCase):

    def testSkins(self):
        portal_skins = self.portal.portal_skins.objectIds()
        skins = (
            'ploneboard_images',
            'ploneboard_scripts',
            'ploneboard_templates',
        )
        for skin in skins:
            self.failUnless(skin in skins)

    def testPortalTypes(self):
        portal_types = self.portal.portal_types.objectIds()
        content_types = (
            'Ploneboard',
            'PloneboardForum',
            'PloneboardConversation',
            'PloneboardComment',
        )
        for content_type in content_types:
            self.failUnless(content_type in portal_types)

    def testTools(self):
        from Products.Ploneboard.config import PLONEBOARD_TOOL, PLONEBOARD_CATALOG
        tool_names = (
            PLONEBOARD_TOOL, 
            PLONEBOARD_CATALOG,
            )
        for tool_name in tool_names:
            self.failUnless(tool_name in self.portal.objectIds())

    def testObjectImplements(self):
        from Products.Ploneboard.PloneboardCatalog import object_implements
        from Products.Ploneboard.config import PLONEBOARD_CATALOG
        mt = getattr(self.portal, PLONEBOARD_CATALOG)
        self.failUnlessEqual(object_implements(mt, self.portal), object_implements(self.portal.portal_catalog, self.portal))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

if __name__ == '__main__':
    framework()
