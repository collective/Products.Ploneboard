##############################################################################
#
# Copyright (c) 2002-2003 Ingeniweb SARL
#
# This software is subject to the provisions of the GNU Public License,
# Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
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
    __version_file_ = open(os.path.abspath(os.path.dirname(__file__)) + '/version.txt', 'r+', )
    version__ = __version_file_.read()[:-1]
else:
    version__ = "(UNKNOWN)"

# Max allowrd users or groups to enable tree view
MAX_TREE_USERS_AND_GROUPS = 50

