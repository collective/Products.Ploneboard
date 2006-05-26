#
# Ploneboard tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from zope.testing import doctest
from zope.app.tests import placelesssetup

setup = placelesssetup.setUp
teardown = placelesssetup.tearDown

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.Ploneboard.browser',
                             setUp=setup, tearDown=teardown),))

if __name__ == '__main__':
    framework()
