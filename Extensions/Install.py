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
from Products.CMFMember.Extensions.Workflow \
    import setupWorkflow, workflow_transfer
#from Products.CMFMember.Extensions.SimpleWorkflow \
#    import setupWorkflow

import sys

TYPE_NAME = 'Member'

def getCMFVersion(self):
    return self.Control_Panel.Products.CMFCore.version[4:]

def installMember(self, out):
    installTypes(self, out, CMFMember.listTypes(CMFMember.PKG_NAME), CMFMember.PKG_NAME)
    wf_tool = getToolByName(self, 'portal_workflow')
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    wf_tool.setChainForPortalTypes((TYPE_NAME,), 'member_workflow')
    wf_tool.updateRoleMappings()


def replaceTools(self, out, convert=1):
    typestool=getToolByName(self, 'portal_types')
    if not hasattr(typestool, 'MemberArea'):
        # For a object to be displayed in contentValues it must be registered with the
        # portal_types tool.  So lets do this and make the MemberDataTool not addable.
        # XXX This seems kind of evil.
        from Products.CMFCore.TypesTool import FactoryTypeInformation
        typestool.manage_addTypeInformation(FactoryTypeInformation.meta_type, id='MemberArea', 
          typeinfo_name='CMFCore: Portal Folder')
        memberarea=typestool.MemberArea
        memberarea.content_meta_type='CMFMember Tool'
        memberarea.icon = 'folder_icon.gif'
        _actions=memberarea._cloneActions()
        for action in _actions:
            try:
                if action['id']=='view':
                    action['action']='folder_contents'
            except AttributeError:
                if action.id=='view':
                    action.action=Expression(text='string:folder_contents')
        memberarea._actions=_actions
        memberarea.global_allow = 0  # make MemberArea not implicitly addable

    portal = getToolByName(self, 'portal_url').getPortalObject()
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    if memberdata_tool.__class__ != CMFMember.MemberDataTool.MemberDataTool:

#        # purge orphans
#        if memberdata_tool.getMemberDataContents()[0]['orphan_count'] > 0:
#            memberdata_tool.pruneMemberDataContents()

        membership_tool = getToolByName(self, 'portal_membership')
        
        oldMemberData = {}
        for id in memberdata_tool._members.keys():
            user = _getUserById(self, id)
            if user is not None:
                data = {}
                data['user'] = user
                from Products.Archetypes.Field import Image
                p = membership_tool.getPersonalPortrait(id)
                img_id = p.id
                if callable(p.id):
                    img_id = p.id()
                img_data = getattr(p, 'data', getattr(p, '_data', ''))
                data['portrait'] = Image(img_id, img_id, str(img_data), p.getContentType())
                properties = {}
                m = memberdata_tool.wrapUser(user)
                for id in memberdata_tool.propertyIds():
                    properties[id] = m.getProperty(id)
                data['properties'] = properties
                oldMemberData[user.getUserName()] = data

        # replace the old tools
        memberdata_tool = None
        # delete the old tools
        if hasattr(portal, 'portal_memberdata'):
            portal.manage_delObjects(['portal_memberdata'])

        addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
        addTool(CMFMember.PKG_NAME + ' Tool', None)

        memberdata_tool = getToolByName(self, 'portal_memberdata')
        memberdata_tool._setPortalTypeName('MemberArea')
        if hasattr(portal, 'portal_registration'):
            portal.manage_delObjects(['portal_registration'])
        addTool('CMFMember Registration Tool', None)
        if hasattr(portal, 'portal_membership'):
            portal.manage_delObjects(['portal_membership'])
        addTool('CMFMember Membership Tool', None)

        factory = MemberDataTool.getMemberFactory(memberdata_tool, TYPE_NAME)

        workflow_tool = getToolByName(self, 'portal_workflow')
        for id in oldMemberData.keys():
            factory(id)
            new_member = memberdata_tool.get(id)
            new_member._migrate(oldMemberData[id], ['portrait'], out)
            workflow_tool.doActionFor(new_member, 'migrate') # put member in registered state without sending registration mail


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


def setupRegistration(self, out):
    # Allow Anonymous to add objects to memberdata tool
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    memberdata_tool.manage_permission(CMFCorePermissions.AddPortalContent, ('Anonymous','Authenticated','Manager',), acquire=1 )

    # wire up join action to new machinery
    registration_tool=getToolByName(self, 'portal_registration')
    actions=registration_tool._cloneActions()
    for action in actions:
        if action.id=='join':
            action.action=Expression('string:${portal_url}/createMember')
    registration_tool._actions=tuple(actions)


def setupMembership(self, out):
    # wire up personalize action to new machinery
    membership_tool=getToolByName(self, 'portal_membership')
    actions=membership_tool._cloneActions()
    for action in actions:
        if action.id=='preferences':
            action.action=Expression('string:${portal_url}/portal_memberdata/${portal/portal_membership/getAuthenticatedMember}/portal_form/personalize_form')
    membership_tool._actions=tuple(actions)


def setupNavigation(self, out, type_name):
    nav_tool = getToolByName(self, 'portal_navigation')

    nav_tool.addTransitionFor('default', 'join_form', 'failure', 'join_form')
    nav_tool.addTransitionFor('default', 'join_form', 'success', 'script:do_register')
    nav_tool.addTransitionFor('default', 'do_register', 'success', 'registered')

    nav_tool.addTransitionFor('default', 'personalize_form', 'failure', 'personalize_form')
    nav_tool.addTransitionFor('default', 'personalize_form', 'success', 'script:content_edit')

    form_tool = getToolByName(self, 'portal_form')
    form_tool.setValidators('join_form', ['validate_base'])
    form_tool.setValidators('personalize_form', ['validate_base'])


def installSkins(self, out):
    install_subskin(self, out, CMFMember.GLOBALS, 'skins')


def installPortalFactory(self, out):
    if hasattr(self, 'portal_factory'):
        self.manage_delObjects(['portal_factory'])
    self.manage_addProduct[CMFMember.PKG_NAME].manage_addTool('Plone Factory Tool', None)

    site_props = self.portal_properties.site_properties
    if not hasattr(site_props,'portal_factory_types'):
        site_props._setProperty('portal_factory_types',('Member',), 'lines')

    from Products.CMFCore.TypesTool import FactoryTypeInformation
    types_tool = getToolByName(self, 'portal_types')
    types_tool.manage_addTypeInformation(FactoryTypeInformation.meta_type,
                                         id='TempFolder', 
                                         typeinfo_name='CMFCore: Portal Folder')
    tempfolder = types_tool.TempFolder
    tempfolder.content_meta_type='TempFolder'
    tempfolder.icon = 'folder_icon.gif'
    tempfolder.global_allow = 0  # make TempFolder not implicitly addable
    tempfolder.allowed_content_types=(types_tool.listContentTypes())


def install(self):
    out=StringIO()

    setupWorkflow(self, out)
    installMember(self, out)
    replaceTools(self, out)
    installSkins(self, out)
    setupRegistration(self, out)
    setupMembership(self, out)
    setupNavigation(self, out, 'Member')
    installPortalFactory(self, out)
    
    print >> out, 'Successfully installed %s' % CMFMember.PKG_NAME
    import sys
    sys.stdout.write(out.getvalue())
    
    return out.getvalue()
