from Products.Archetypes.debug import log, log_exc
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from StringIO import StringIO

import Products.CMFMember as CMFMember
import Products.CMFMember.MemberDataTool as MemberDataTool
from Products.CMFMember.Extensions.Workflow import setupWorkflow
import pdb
import sys


def installMember(self, out):
    installTypes(self, out, CMFMember.listTypes(CMFMember.PKG_NAME), CMFMember.PKG_NAME)


def replaceTools(self, out, convert=1):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    catalog = getToolByName(self, 'portal_catalog')

    _v_tempFolder = PortalFolder('temp').__of__(self)
#    catalog.unindexObject(_v_tempFolder)

    factory = MemberDataTool.getMemberFactory(_v_tempFolder)

    for u in portal.acl_users.getUsers():
        old_member = memberdata_tool.wrapUser(u)
        id = old_member.getMemberId()
        factory(id)
        new_member = getattr(_v_tempFolder, id)
        new_schema = new_member.Schema()

        for new_field in new_schema.fields():
            if new_field.name not in ['password', 'roles', 'domains']: # fields managed by user object
                try:
                    value = _getOldValue(old_member, new_member, new_field.name, out)
                    _setNewValue(new_member, new_field.name, value, out)
                    print >> out, '%s.%s = %s' % (str(old_member.getMemberId()), new_field.name, str(value))
                except:
                    pass
        catalog.unindexObject(new_member)  # don't index stuff in temp folder

    memberdata_tool = None
    # delete the old tools
    if hasattr(portal, 'portal_memberdata'):
        portal.manage_delObjects(['portal_memberdata'])
    if hasattr(portal, 'portal_registration'):
        portal.manage_delObjects(['portal_registration'])

    addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
    addTool(CMFMember.PKG_NAME + ' Tool', None)
    addTool('Default Registration Tool', None)

    memberdata_tool = getToolByName(self, 'portal_memberdata')
    registration_tool = getToolByName(self, 'portal_registration')
    

    # move the old members into the new memberdata tool
    for m in _v_tempFolder.objectValues():
        memberdata_tool.registerMemberData(m, m.id)
        member = memberdata_tool.getMemberById(m.id)
        catalog.reindexObject(member)

    # XXX eventually should copy over workflow state, references, etc to allow for schema upgrades

    # Allow Anonymous to add objects to memberdata tool
    memberdata_tool.manage_permission(CMFCorePermissions.AddPortalContent, ('Anonymous','Authenticated','Manager',), acquire=1 )
    # Only allow Member objects to be added in the memberdata tool
    portal.manage_permission(CMFMember.ADD_PERMISSION, (), acquire=0)
    memberdata_tool = getToolByName(portal, 'portal_memberdata')
    memberdata_tool.manage_permission(CMFMember.ADD_PERMISSION, ('Manager',), acquire=1)

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


    # monkey patch portal_registration's mail_password function
#    registration_tool = getToolByName(portal, 'portal_registration')
#    registration_tool.mailPassword = memberdata_tool.mailPassword


def _getOldValue(old, new, id, out):
    old_schema = getattr(old, 'Schema', None)
    if old_schema is not None:
        old_schema = old_schema()

    new_schema = new.Schema()

    if old_schema:
        old_field = old_schema.get(id, None)
        if old_field:
            accessor = getattr(old, old_field.accessor, None)
            if accessor is not None:
                return accessor()
    new_field = new_schema.get(id)
    try:
        accessor = getattr(old, new_field.accessor)
        if callable(accessor):
            return accessor()
        return accessor
    except:
        pass
    
    try:
        return getattr(old_member, id)
    except:
        pass
    
    print >> out, 'Unable to get property %s from member %s\n' % (new_field.name, old.getMemberId())
    raise ValueError
    
def _setNewValue(new, id, value, out):
    new_schema = new.Schema()
    new_field = new_schema.get(id)
    if new_field.mutator is not None:
        mutator = getattr(new, new_field.mutator)
        mutator(value)
        return
    if hasattr(new, id):
        setattr(new, id, value)
        return
    print >> out, 'Unable to set property %s from member %s\n' % (new_field.name, new.getMemberId())
    raise ValueError


def install(self):
    out=StringIO()
    
    installMember(self, out)
    setupWorkflow(self, out)
    replaceTools(self, out)
    
    print >> out, 'Successfully installed %s' % CMFMember.PKG_NAME
    import sys
    sys.stdout.write(out.getvalue())
    
    return out.getvalue()
