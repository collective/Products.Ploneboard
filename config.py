"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: config.py,v 1.7 2004/11/07 21:52:50 brcwhit Exp $
"""

SKINS_DIR = 'skins'
GLOBALS = globals()
PROJECT_NAME = PKG_NAME = 'ATSchemaEditorNG'

# Permissions
ManageSchemaPermission = 'ATSE: Manage schema'

# Update mode
# True: Schema Editor changes are not persistent.
# The Schema of the object is kept in sync with
# the one defined on the filesystem.
# ATTENTION: Setting this property to True can
# lead to a complete data loss!!
# Never activate it on production systems
ALWAYS_SYNC_SCHEMA_FROM_DISC = False
