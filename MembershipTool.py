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
            #member = apply(member.accessor('portrait'), portrait)
            return member.getPortrait()
        except AttributeError:
            member = getattr(portal, self.default_portrait)
#            member = portal.restrictedTraverse(self.default_portrait)
        return member

    def changeMemberPortrait(self, portrait, member_id=None):
        """Override Plone's changeMemberPortrait method to use
        CMFMember's portrait management"""
        if not member_id:
            return
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        member = memberdata_tool.get(member_id, None)
        if member:
            member.setPortrait(portrait)
            #apply(member.mutator('portrait'), portrait)


    def searchForMembers( self, REQUEST=None, **kw ):
        """ """
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        return memberdata_tool.searchForMembers(REQUEST, **kw)

    def createMemberarea(self, member_id):
        """ created hook for 'preCreateMemberArea' and 'postCreateMemberArea'
            if you provide methods of PythonScripts with these names, they will 
            be called at the begin and end of createMemberData
            
            if preCreateMemberArea returns 1 the normal createMemberArea will be
            called. otherwise it is skipped.
        """
        # if preCreateMemberArea returns false,
        # no further creation of the member area takes place

        # do not create member_area for groups
        if member_id in self.portal_groups.listGroupIds():
            return
        
        pre = getattr(self, 'preCreateMemberArea', None)
        createarea = 1
        if pre:
            createarea = pre(member_id=member_id)
        if createarea:
            BaseTool.createMemberarea(self, member_id)
        post = getattr(self, 'postCreateMemberArea', None)
        if post:
            post(member_id=member_id)

    security.declarePrivate('addMember')
    def addMember(self, id, password, roles, domains, properties=None):
        '''Adds a new member to the user folder.  Security checks will have
        already been performed.  Called by portal_registration.
        '''
        
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        memberdata_tool.invokeFactory('Member',id)
        member=getattr(memberdata_tool.aq_explicit,id)
        member.edit(password=password,roles=roles,domains=domains,**(properties or {}))

    def listMembers(self):
         '''Gets the list of all members.
         '''
         members = BaseTool.listMembers(self)
         groups = []
         # can we allways asume that there is a groups_tool ??
         try:
             groups = self.portal_groups.listGroupIds()
             result = []
             for member in members:
                 if member.getUser().getUserName() in groups:
                     continue
                 result.append(member)
         except:
             result = members
         return result




InitializeClass(MembershipTool)
