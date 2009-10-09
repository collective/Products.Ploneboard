"""Ploneboard functional doctests.  This module collects all *.txt
files in the tests directory and runs them. (stolen from Plone)
"""

import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.Ploneboard.config import GLOBALS

# Load products
from Products.Ploneboard.tests.PloneboardTestCase import PloneboardFunctionalTestCase

REQUIRE_TESTBROWSER = ['MemberPostingForum.txt', 'MemberOnlyForum.txt', 
                        'MemberEditsComment.txt', 'AdminLocksBoard.txt',
                        'FreeForAllForum.txt', 'ModeratedForum.txt']

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]

def list_nontestbrowser_tests():
    return [filename for filename in list_doctests()
            if os.path.basename(filename) not in REQUIRE_TESTBROWSER]

def test_suite():

    # BBB: We can obviously remove this when testbrowser is Plone
    #      mainstream, read: with Five 1.4.
    try:
        import Products.Five.testbrowser
    except ImportError:
        print >> sys.stderr, ("WARNING: testbrowser not found - you probably"
                              "need to add Five 1.4 to the Products folder. "
                              "testbrowser tests skipped")
        filenames = list_nontestbrowser_tests()
    else:
        filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.Ploneboard.tests',
               test_class=PloneboardFunctionalTestCase)
         for filename in filenames]
        )
