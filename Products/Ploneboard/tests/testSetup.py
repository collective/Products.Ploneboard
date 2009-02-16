#
# Ploneboard tests
#

from Products.Ploneboard.tests import PloneboardTestCase

# Catch errors in Install
from Products.Ploneboard.Extensions import Install

from Products.CMFCore.utils import getToolByName

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
        from Products.Ploneboard.config import PLONEBOARD_TOOL
        tool_names = (
            PLONEBOARD_TOOL,
            )
        for tool_name in tool_names:
            self.failUnless(tool_name in self.portal.objectIds())

    def testTransforms(self):
        from Products.Ploneboard.config import PLONEBOARD_TOOL
        tool = getToolByName(self.portal, PLONEBOARD_TOOL)
        transforms = [t for t in tool.getEnabledTransforms()]
        self.failUnless('safe_html' in transforms)
        self.failUnless('text_to_emoticons' in transforms)
        self.failUnless('url_to_hyperlink' in transforms)

    def testCatalogIndex(self):
        ct = getToolByName(self.portal, 'portal_catalog') 
        self.failUnless('object_provides' in ct.indexes())
        self.failUnless('num_comments' in ct.indexes())
        self.failUnless('num_comments' in ct.schema())

    def testPortalFactorySetup(self):
        portal_factory = getToolByName(self.portal, 'portal_factory') 
        factoryTypes = portal_factory.getFactoryTypes().keys()
        for t in ['Ploneboard', 'PloneboardComment', 'PloneboardConversation', 'PloneboardForum']:
            self.failUnless(t in factoryTypes)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
