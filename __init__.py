"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: __init__.py,v 1.1 2004/09/12 07:27:20 ajung Exp $
"""

from Products.CMFCore.DirectoryView import registerDirectory
from config import SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR, GLOBALS)
