from Products.CMFCore.CMFCorePermissions import SetOwnPassword, ManagePortal
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFPlone.MembershipTool import MembershipTool as BaseTool
from Products.CMFMember.MemberPermissions import VIEW_PUBLIC_PERMISSION
from Products.Archetypes.utils import OrderedDict
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
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
        default_portrait = getattr(portal, self.default_portrait)
        if not member_id:
            return default_portrait

        memberdata_tool = getToolByName(self, 'portal_memberdata')
        member = None
        try:
            member = memberdata_tool.get(member_id)
            if verifyPermission and not _checkPermission(VIEW_PUBLIC_PERMISSION, member):
                return default_portrait
            portrait = member.getPortrait()
            if portrait:
                return portrait
        except AttributeError:
            pass
        return default_portrait

    def changeMemberPortrait(self, portrait, member_id=None):
        """Override Plone's changeMemberPortrait method to use
        CMFMember's portrait management"""
        if not member_id:
            return
        memberdata_tool = getToolByName(self, 'portal_memberdata')
        member = memberdata_tool.get(member_id, None)
        if member:
            member.setPortrait(portrait)

    def searchForMembers( self, REQUEST=None, **kw ):
        """
        here for backwards compatibility; member searching is better
        accomplished using the member_catalog, which this ultimately
        delegates to
        """
        if REQUEST:
            param = REQUEST
        else:
            param = kw

        # mapping from older lookup names to the indexes that exist
        # in the member_catalog
        key_map = {'name': 'getId',
                   'email': 'getEmail',
                   'roles': 'getFilteredRoles',
                   'last_login_time': 'getLastLoginTime',
                   }
        for key in key_map:
            if param.has_key(key):
                param[key_map[key]] = param.pop(key)
                
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
        if hasattr(self, 'portal_groups') and member_id in self.portal_groups.listGroupIds():
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

        if hasattr(self, 'portal_memberdata'):
            memberdata_container = self.portal_memberdata
            member_type = 'Member'
            typeName = str(memberdata_container.getTypeName())
            if typeName:
                member_type = typeName
            memberdata_container.invokeFactory(member_type,id)
            member=getattr(memberdata_container.aq_explicit,id)
            member.edit(password=password,roles=roles,domains=domains,**(properties or {}))


    def getMemberById(self, id):
        ''' overload of CMFCore.MembershipTool.getMemberById, returns None if member doesnt exist '''
        if hasattr(self, 'portal_memberdata'):
            memberdata_container = self.portal_memberdata
            member=getattr(memberdata_container.aq_explicit,id,None)
            
        if member is not None:
            return member

        # if no member found, try to find the user
        u = self.acl_users.getUserById(id, None)
        if u is not None:
            # wrap the user and return a new member
            u = self.wrapUser(u)
        return u


    security.declareProtected(SetOwnPassword, 'setPassword')
    def setPassword(self, password, domains=None):
        '''Allows the authenticated member to set his/her own password.
        '''
        try:
            BaseTool.setPassword(self, password, domains)
            member = self.getAuthenticatedMember()
            member._setPassword(password)
        except (errorMsg, errorComment):
            raise errorMsg, errorComment

    security.declarePublic('areUsersAutomatic')
    def areUsersAutomatic(self):
        return false

InitializeClass(MembershipTool)
