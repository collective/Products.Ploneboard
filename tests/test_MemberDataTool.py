from unittest import TestCase, TestSuite, makeSuite, main

import Zope
root = Zope.app()
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

import Products.CMFMember
from Products.CMFMember.MemberDataTool import MemberDataTool
from Products.CMFMember.types.Member import Member as MemberData


class MemberDataToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import portal_memberdata as IMemberDataTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMemberDataTool, MemberDataTool)
        verifyClass(IActionProvider, MemberDataTool)

class MemberDataTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import MemberData as IMemberData

        verifyClass(IMemberData, MemberData)


def test_suite():
    return TestSuite((
        makeSuite( MemberDataToolTests ),
        makeSuite( MemberDataTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
