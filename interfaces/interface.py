"""

$Id: interface.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

try:
    # Zope >= 2.6
    from Interface import Interface, Attribute
except ImportError:
    # Zope < 2.6
    try:
        from Interface import Base as Interface, Attribute
    except ImportError:
        class Interface:
            """dummy interface class
            """
            pass

        class Attribute:
            """dummy attribute class
            """
            def __init__(self, doc):
                self.doc = doc
                
            def __repr__(self):
                return self.doc
