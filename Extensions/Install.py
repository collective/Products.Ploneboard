
"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: Install.py,v 1.1 2004/09/12 07:27:25 ajung Exp $
"""


def install(self):                                       
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
