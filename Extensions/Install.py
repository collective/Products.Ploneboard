
"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: Install.py,v 1.3 2004/09/12 08:59:34 ajung Exp $
"""

from cStringIO import StringIO
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.ATSchemaEditorNG.config import GLOBALS, PROJECTNAME

def install(self):                                       
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
