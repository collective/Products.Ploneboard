import os, sys, string
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase


class TestMemberSearch(CMFMemberTestCase.CMFMemberTestCase):

    def testInstallationofMemberCatalog(self):
        self.failUnless(hasattr(self.portal, 'member_catalog'))
        self.failUnless('review_state' in self.portal.member_catalog.indexes())
        cat_indexes = self.portal.member_catalog.indexes()
        schema = self.portal.archetype_tool.lookupType('CMFMember','Member')['schema']
        accessors = [x.accessor  for x in schema.fields() if x.index]
        accessors.append('review_state')
        accessors.sort()
        cat_indexes.sort()
        self.assertEqual(cat_indexes, accessors)


if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMemberSearch))
        return suite
