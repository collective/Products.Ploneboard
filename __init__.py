"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: __init__.py,v 1.2 2004/09/27 13:32:47 spamsch Exp $
"""

from Products.CMFCore.DirectoryView import registerDirectory
from config import SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR, GLOBALS)

# make refresh possible
from SchemaEditor import SchemaEditor
from ParentManagedSchema import ParentManagedSchema
