from Products.Archetypes.debug import log, log_exc
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.Expression import Expression
from StringIO import StringIO

import Products.CMFMember as CMFMember
import Products.CMFMember.MemberDataTool as MemberDataTool
from Products.CMFMember.Extensions.Workflow import setupWorkflow, workflow_transfer
import pdb
import sys


def installMember(self, out):
    installTypes(self, out, CMFMember.listTypes(CMFMember.PKG_NAME), CMFMember.PKG_NAME)


def replaceTools(self, out, convert=1):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    if memberdata_tool.__class__ != CMFMember.MemberDataTool:
        catalog = getToolByName(self, 'portal_catalog')

        _v_tempFolder = PortalFolder('temp').__of__(self)

        factory = MemberDataTool.getMemberFactory(_v_tempFolder)

        for u in portal.acl_users.getUsers():
            old_member = memberdata_tool.wrapUser(u)
            id = old_member.getMemberId()
            factory(id)
            new_member = getattr(_v_tempFolder, id)
            new_member._migrate(old_member, out)
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

        # XXX This seems kind of evil.
        # For a object to be displayed in contentValues it must be registered with the
        # portal_types tool.  So lets do this and make the MemberDataTool not addable.
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
        memberarea.allowed_content_types=(CMFMember.TYPE_NAME,)
        memberarea.global_allow = 0  # make MemberArea not implicitly addable
        memberdata_tool._setPortalTypeName('MemberArea')

# Migrate members when changing member type
# 1) rename old member to some temp name
# 2) create new member with old id
# 3) transfer user assets to new member
# 4) delete old member
def migrateMembers(self):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    workflow_tool = getToolByName(self, 'portal_workflow')

    factory = MemberDataTool.getMemberFactory(_v_tempFolder)
    for m in memberdata_tool.objectIds():
        old_member = memberdata_tool.get(m)
        temp_id = m + 'temp_'
        while memberdata_tool.get(temp_id):
            temp_id = '_' + temp_id
            
        memberdata_tool.manage_renameObj(old_member, temp_id)
        factory(m)
        # copy over old member attributes
        new_member._migrate(old_member, out)

        # copy workflow state
        old_member_state = workflow_tool.getInfoFor(old_member, 'review_state', '')
        print >> out, 'state = %s' % (old_member_state,)
        transitions = workflow_transfer.get(old_member_state, [])
        print >> out, 'transitions = %s' % (str(transitions),)
        for t in transitions:
            workflow_tool.doActionFor(ob, t)

        # transfer old user attributes
        m._changeUserInfo(self, portal, temp_id, m)

        memberdata_tool.manage_delObjects(temp_id)
    

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

    installMember(self, out)
    setupWorkflow(self, out)
    replaceTools(self, out)
    
    print >> out, 'Successfully installed %s' % CMFMember.PKG_NAME
    import sys
    sys.stdout.write(out.getvalue())
    
    return out.getvalue()