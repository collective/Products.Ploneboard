
"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: Install.py,v 1.2 2004/09/12 08:57:38 ajung Exp $
"""

from cStringIO import StringIO

def install(self):                                       
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
