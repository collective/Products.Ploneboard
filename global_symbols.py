##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL
#
##############################################################################

"""GroupUserFolder product"""
import os


# Check if we have to be in debug mode
import Log
if os.path.isfile(os.path.abspath(os.path.dirname(__file__)) + '/debug.txt'):
    Log.LOG_LEVEL = Log.LOG_DEBUG
else:
    Log.LOG_LEVEL = Log.LOG_NOTICE

from Log import *
Log = Log
Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))


# Retreive version
if os.path.isfile(os.path.abspath(os.path.dirname(__file__)) + '/version.txt'):
    __version_file_ = open(os.path.abspath(os.path.dirname(__file__)) + '/version.txt', 'r', )
    version__ = __version_file_.read()[:-1]
else:
    version__ = "(UNKNOWN)"

# Batching range for ZMI pages
MAX_USERS_PER_PAGE = 100

# Max allowrd users or groups to enable tree view
MAX_TREE_USERS_AND_GROUPS = 100

# Users/groups tree cache time (in seconds)
# This is used in management screens only
TREE_CACHE_TIME = 10

# List of user names that are likely not to be valid user names.
# This list is for performance reasons in ZMI views. If some actual user names
# are inside this list, management screens won't work for them but they
# will still be able to authenticate.
INVALID_USER_NAMES = [
    'BASEPATH1', 'BASEPATH2', 'BASEPATH3', 'a_', 'URL', 'acl_users', 'misc_',
    'management_view', 'management_page_charset', 'REQUEST', 'RESPONSE',
    'MANAGE_TABS_NO_BANNER', 'tree-item-url', 'SCRIPT_NAME', 'n_', 'help_topic',
    'Zope-Version', 'target', 
    ]


