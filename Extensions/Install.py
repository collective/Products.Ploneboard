from Products.Archetypes.debug import log, log_exc
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

import Products.CMFMember as CMFMember
import Products.CMFMember.MemberDataTool as MemberDataTool
from Products.CMFMember.Extensions.Workflow import setupWorkflow, workflow_transfer
import pdb
import sys

TYPE_NAME = 'Member'

def installMember(self, out):
    installTypes(self, out, CMFMember.listTypes(CMFMember.PKG_NAME), CMFMember.PKG_NAME)
    wf_tool = getToolByName(self, 'portal_workflow')
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    wf_tool.setChainForPortalTypes((TYPE_NAME,), 'member_workflow')
    wf_tool.updateRoleMappings()


def replaceTools(self, out, convert=1):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    if memberdata_tool.__class__ != CMFMember.MemberDataTool:
        # For a object to be displayed in contentValues it must be registered with the
        # portal_types tool.  So lets do this and make the MemberDataTool not addable.
        # XXX This seems kind of evil.
        typestool=getToolByName(self, 'portal_types')
        from Products.CMFCore.TypesTool import FactoryTypeInformation
        typestool.manage_addTypeInformation(FactoryTypeInformation.meta_type, id='MemberArea', 
          typeinfo_name='CMFCore: Portal Folder')
        memberarea=typestool.MemberArea
        memberarea.content_meta_type='CMFMember Tool'
        _actions=memberarea._cloneActions()
        for action in _actions:
            if action['id']=='view':
                action['action']='folder_contents'
        memberarea._actions=_actions
        memberarea.global_allow = 0  # make MemberArea not implicitly addable

#        # purge orphans
#        if memberdata_tool.getMemberDataContents()[0]['orphan_count'] > 0:
#            memberdata_tool.pruneMemberDataContents()

        catalog = getToolByName(self, 'portal_catalog')
        _v_tempFolder = PortalFolder('temp').__of__(self)
        factory = MemberDataTool.getMemberFactory(_v_tempFolder, TYPE_NAME)

#        membership_tool= getToolByName(self, 'portal_membership')
#        user_list = membership_tool.listMemberIds()
#        for u in user_list:
        for u in memberdata_tool._members.keys():
            user = _getUserById(self, u)
            if user is not None:
                old_member = memberdata_tool.wrapUser(user)
                id = old_member.getMemberId()
                factory(id)
                new_member = getattr(_v_tempFolder, id)
                new_member._migrate(old_member, ['portrait'], out)
                catalog.unindexObject(new_member)  # don't index stuff in temp folder

        memberdata_tool = None
        # delete the old tools
        if hasattr(portal, 'portal_memberdata'):
            portal.manage_delObjects(['portal_memberdata'])
        if hasattr(portal, 'portal_registration'):
            portal.manage_delObjects(['portal_registration'])
        if hasattr(portal, 'portal_membership'):
            portal.manage_delObjects(['portal_membership'])

        addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
        addTool(CMFMember.PKG_NAME + ' Tool', None)
        addTool('CMFMember Registration Tool', None)
        addTool('CMFMember Membership Tool', None)

        memberdata_tool = getToolByName(self, 'portal_memberdata')
        registration_tool = getToolByName(self, 'portal_registration')
    
        # move the old members into the new memberdata tool
        for m in _v_tempFolder.objectValues():
            memberdata_tool.registerMemberData(m, m.id)
            member = memberdata_tool.get(m.id)
            catalog.reindexObject(member)

        memberdata_tool._setPortalTypeName('MemberArea')
        memberarea.allowed_content_types=(memberdata_tool.typeName,)

    

def _getUserFolderForUser(self, id=None):
    f = getToolByName(self, 'portal_url').getPortalObject()
    if id is None:
        return f.acl_users
    while 1:
        if not hasattr(f, 'objectIds'):
            return
        if 'acl_users' in f.objectIds():
            if hasattr(f.acl_users, 'getUser'):
                user = f.acl_users.getUser(id)
                if user is not None:
                    return f.acl_users
        if hasattr(f, 'getParentNode'):
            f = f.getParentNode()
        else:
            return None


def _getUserById(self, id):
    """A utility method for finding a user by searching through
    portal.acl_users as well as the acl_users folders for all
    zope folders containing portal.
    
    Returns the user in the acquisition context of its containing folder"""
    acl_users = _getUserFolderForUser(self, id)
    if acl_users is None:
        return None
    return acl_users.getUser(id).__of__(acl_users)


def setupRegistration(self):
    # Allow Anonymous to add objects to memberdata tool
    memberdata_tool.manage_permission(CMFCorePermissions.AddPortalContent, ('Anonymous','Authenticated','Manager',), acquire=1 )

    # wire up join action to new machinery
    registration_tool=getToolByName(portal, 'portal_registration')
    actions=registration_tool._cloneActions()
    for action in actions:
            if action.id=='join':
                action.action=Expression('string:${portal_url}/portal_memberdata/createObject?type_name=Member')
    registration_tool._actions=tuple(actions)


def install(self):
    out=StringIO()

    setupWorkflow(self, out)
    installMember(self, out)
    replaceTools(self, out)
    
    print >> out, 'Successfully installed %s' % CMFMember.PKG_NAME
    import sys
    sys.stdout.write(out.getvalue())
    
    return out.getvalue()