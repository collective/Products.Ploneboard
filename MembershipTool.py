from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFPlone.MembershipTool import MembershipTool as BaseTool
from Products.CMFMember.MemberPermissions import VIEW_PUBLIC_PERMISSION

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

class MembershipTool( BaseTool ):
    meta_type='CMFMember Membership Tool'
    security = ClassSecurityInfo()
    plone_tool = 1

    def getPersonalPortrait(self, member_id=None, verifyPermission=0):
        """Returns the Portait for a member_id"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        if not member_id:
            return getattr(portal, self.default_portrait)

        memberdata_tool = getToolByName(self, 'portal_memberdata')
        member = None
        try:
            member = memberdata_tool.get(member_id)
            if verifyPermission and not _checkPermission(VIEW_PUBLIC_PERMISSION, member):
                return None
            return apply(member.accessor('portrait'), ())
        except AttributeError:
            member = getattr(portal, self.default_portrait)
        return member

    def changeMemberPortrait(self, portrait, member_id=None):
        """Override Plone's changeMemberPortrait method to use
        CMFMember's portrait management"""
        if not member_id:
            return
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        member = memberdata_tool.get(member_id, None)
        if member:
            apply(member.mutator('portrait'), portrait)


    def searchForMembers( self, REQUEST=None, **kw ):
        """ """
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        return memberdata_tool.searchForMembers(REQUEST, **kw)

InitializeClass(MembershipTool)


