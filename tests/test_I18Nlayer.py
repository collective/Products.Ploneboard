from unittest import TestCase, TestSuite, makeSuite, main
import Zope
Zope.startup()

from Products.I18NLayer.I18NLayer import I18NLayer
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

class Tests(TestCase):

    def test_interface(self):
        from Products.Archetypes.interfaces.base import IBaseFolder
        print verifyClass(IBaseFolder, I18NLayer)

def test_suite():
    return TestSuite((
        makeSuite( Tests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
