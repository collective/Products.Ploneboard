import sys
from cStringIO import StringIO

# Load fixture
from Testing import ZopeTestCase

# Install our product
ZopeTestCase.installProduct('CMFSquidTool')

from Products.CMFPlone.tests import PloneTestCase

class BaseTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def assertStructEquals(self, got, expected):
        _got = StringIO()
        _expected = StringIO()
        pprint(got, _got)
        pprint(expected, _expected)
        _got = _got.getvalue().splitlines()
        _expected = _expected.getvalue().splitlines()
        diff = unified_diff(_expected, _got)
        self.failUnless(got == expected, '\n'.join(diff))
