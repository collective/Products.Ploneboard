import doctest
import glob
import os
import unittest

from App.Common import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.Ploneboard.config import GLOBALS

# Load products
from Products.Ploneboard.tests.PloneboardTestCase import PloneboardFunctionalTestCase

REQUIRE_TESTBROWSER = ['MemberPostingForum.txt', 'MemberOnlyForum.txt', 
                        'MemberEditsComment.txt', 'AdminLocksBoard.txt',
                        'FreeForAllForum.txt', 'ModeratedForum.txt']

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]


def test_suite():
    filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.Ploneboard.tests',
               test_class=PloneboardFunctionalTestCase)
         for filename in filenames]
        )
