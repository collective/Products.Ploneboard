"""ATContentTypes tests

$Id: ATCTTestCase.py,v 1.5 2004/06/06 15:36:33 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase

from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore as IMutableDublinCore

class ATCTTestCase(ZopeTestCase.ZopeTestCase):
    """ ATContentTypes test case based on ZopeTestCase"""

    def testDoesImplemendDC(self):
        self.failUnless(IDublinCore.isImplementedBy(self._dummy))
        self.failUnless(IMutableDublinCore.isImplementedBy(self._dummy))
        
    def testDoesImplementATCT(self):
        self.failUnless(IATContentType.isImplementedBy(self._dummy))
        
        