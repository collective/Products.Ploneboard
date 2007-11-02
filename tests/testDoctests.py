#
# Ploneboard tests
#

import unittest
from zope.testing import doctest
from zope.app.testing import placelesssetup

setup = placelesssetup.setUp
teardown = placelesssetup.tearDown

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.Ploneboard.browser',
                             setUp=setup, tearDown=teardown),))

