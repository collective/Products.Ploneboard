from Products.Archetypes.debug import log, log_exc
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
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

    _v_tempFolder = PortalFolder('temp').__of__(self)
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
                    sys.stdout.write('%s.%s = %s\n' % (str(old_member.getMemberId()), new_field.name, str(value)))
                    print >> out, '%s.%s = %s\n' % (str(old_member.getMemberId()), new_field.name, str(value))
                except:
                    pass

    memberdata_tool = None
    # delete the old memberdata tool
    portal.manage_delObjects(['portal_memberdata'])

    ap = portal.manage_addProduct[CMFMember.PKG_NAME]
    addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
    addTool(CMFMember.PKG_NAME + ' Tool', None)
    memberdata_tool = getToolByName(self, 'portal_memberdata')

    # move the old members into the new memberdata tool
    pdb.set_trace()
    for m in _v_tempFolder.objectValues():
        memberdata_tool.registerMemberData(m, m.id)

    # XXX eventually should copy over workflow state, references, etc to allow for schema upgrades

    # Only allow Member objects to be added in the memberdata tool
    portal.manage_permission(CMFMember.ADD_PERMISSION, (), acquire=0)
    memberdata_tool = getToolByName(portal, 'portal_memberdata')
    memberdata_tool.manage_permission(CMFMember.ADD_PERMISSION, ('Manager',), acquire=1)


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