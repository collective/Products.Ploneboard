# -*- coding: iso-8859-15 -*-

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: Install.py,v 1.5 2004/11/02 17:27:48 ajung Exp $
"""

from cStringIO import StringIO
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.ATSchemaEditorNG.config import GLOBALS, PROJECT_NAME

def install(self):                                       
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECT_NAME
    return out.getvalue()
