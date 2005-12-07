#
# Ploneboard tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import PloneboardTestCase

from Products.CMFPlone.utils import _createObjectByType


class TestPloneboard(PloneboardTestCase.PloneboardTestCase):

    def testAddPloneboard(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        self.assertEqual(len(self.portal.contentValues('Ploneboard')), 0)
        # Content creation
        content_id = "board"
        _createObjectByType('Ploneboard', self.portal, content_id)
        self.assertEqual(len(self.portal.contentValues('Ploneboard')), 1)
        self.failUnless(content_id in self.portal.objectIds(), "Ploneboard has not been created or not with the right id")
        content = getattr(self.portal, content_id)

        # Basic checks
        self.assertEqual(content.title, '')
        self.assertEqual(content.id, content_id)
        
    def testRemovePloneboard(self):
        """
        Create new folder in home directory & check its basic properties and behaviour
        """
        self.assertEqual(len(self.portal.contentValues('Ploneboard')), 0)
        # Content creation
        content_id = "board"
        _createObjectByType('Ploneboard', self.portal, content_id)
        self.assertEqual(len(self.portal.contentValues('Ploneboard')), 1)
        self.portal._delObject(content_id)
        self.assertEqual(len(self.portal.contentValues('Ploneboard')), 0)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneboard))
        return suite
