import AccessControl
from Acquisition import aq_base
from Products.CMFPlone import MigrationTool
from Products.CMFMember import VERSION
import Products.CMFMember as CMFMember
import Products.CMFMember.MemberDataContainer as MemberDataContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from StringIO import StringIO

def _migrateTool(portal, toolid, name, attrs):
    orig=getToolByName(portal, toolid)
    portal.manage_delObjects(toolid)
    portal.manage_addProduct['CMFMember'].manage_addTool(name)
    tool = getToolByName(portal, toolid)
    for attr in attrs:
        setattr(tool, attr, aq_base(getattr(aq_base(orig), attr)))
    return aq_base(orig)

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

def pathToUser(portal, path):
    if not path:
        return None
    folder = portal.getPhysicalRoot()
    for p in path[:-1]:
        folder = getattr(folder, p)
    u=folder.getUser(path[-1])
    if u is None:
        return u
    return u.__of__(folder)

def replaceOldMemberDataTool(self):
    typestool=getToolByName(self, 'portal_types')
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if memberdata_tool.__class__.portal_type == 'CMFMember Tool':
        # get old members and move them to new portal_memberdata
        oldMembers = memberdata_tool.objectValues()
        portal.manage_delObjects(['portal_memberdata'])

        addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
        portal.invokeFactory(id='portal_memberdata', type_name='MemberDataContainer')

        memberdata_tool = portal.portal_memberdata
        factory = MemberDataContainer.getMemberFactory(memberdata_tool, 'Member')
        out = StringIO()
        workflow_tool = getToolByName(self, 'portal_workflow')
        for oldMember in oldMembers:
            factory(oldMember.getId())
            new_member = memberdata_tool.get(oldMember.getId())
            new_member._migrate(oldMember, [], out)
            workflow_tool.doActionFor(new_member, 'migrate') # put member in registered state without sending registration mail
            # change ownership for migrated member
            new_member.changeOwnership(new_member.getUser(), 1)
            new_member.manage_setLocalRoles(new_member.getUserName(), ['Owner'])
    
def replaceTools(self, convert=1):
    typestool=getToolByName(self, 'portal_types')
    memberdata_tool = getToolByName(self, 'portal_memberdata')
    portal = getToolByName(self, 'portal_url').getPortalObject()
    #memberdata_tool = portal.portal_memberdata #getToolByName(self, 'portal_memberdata')
    if memberdata_tool.__class__ != CMFMember.MemberDataContainer.MemberDataContainer:

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
        portal.invokeFactory(id='portal_memberdata', type_name='MemberDataContainer')

        memberdata_tool = portal.portal_memberdata

        if hasattr(portal, 'portal_registration'):
            portal.manage_delObjects(['portal_registration'])
        addTool('CMFMember Registration Tool', None)

        _migrateTool(portal, 'portal_registration', 'CMFMember Registration Tool', ['_actions'])
        #_migrateTool(portal, 'portal_catalog', 'Portal CMFMember Catalog Tool', ['_actions', '_catalog'])
        
        catalog = portal.portal_catalog
        catalog.addIndex('indexedUsersWithLocalRoles', 'KeywordIndex')
        catalog.addIndex('indexedOwner', 'FieldIndex')
        catalog.addColumn('indexedOwner')
        catalog.addColumn('indexedUsersWithLocalRoles')
        # XXX be sure to migrate portraits before replacing the membership tool
        if hasattr(portal, 'portal_membership'):
            portal.manage_delObjects(['portal_membership'])
        addTool('CMFMember Membership Tool', None)

        factory = MemberDataContainer.getMemberFactory(memberdata_tool, 'Member')

        workflow_tool = getToolByName(self, 'portal_workflow')
        for id in oldMemberData.keys():
            factory(id)
            new_member = memberdata_tool.get(id)
            new_member._migrate(oldMemberData[id], ['portrait'], out)
            workflow_tool.doActionFor(new_member, 'migrate') # put member in registered state without sending registration mail
            # change ownership for migrated member
            new_member.changeOwnership(new_member.getUser(), 1)
            new_member.manage_setLocalRoles(new_member.getUserName(), ['Owner'])

def updateVersionNumbers(portal):
    tool = getToolByName(portal, 'cmfmember_control')
    tool.setInstanceVersion(CMFMember.VERSION)
    memberdata_tool = portal.portal_memberdata    
    memberdata_tool.setVersion(CMFMember.VERSION)

def migrateUserPath(portal):
    memberdata_tool = portal.portal_memberdata
    for user in memberdata_tool.objectValues():
        if getattr(user,'_userPath', None):
            # no userpath to migrate
            continue
        if not hasattr(user, '_v_user') or user._v_user is None:
            if getattr(user, '_has_user', None):
                user._v_user = (pathToUser(portal, user._userPath),)
            else:
                acl_users = portal.acl_users
                user._v_user = (AccessControl.User.SimpleUser(user.id, user.password, user.roles, user.domains).__of__(acl_users),)
        user.setUser(user._v_user[0])
        
def oneZeroAlpha(portal):
    """ Upgrade from development CMFMember (i.e. from the Plone1_compatible branch)
    to CMFMember 1.0 alpha"""

    replaceOldMemberDataTool(portal)
#    migrateUserPath(portal)
    updateVersionNumbers(portal)
        
if __name__=='__main__':
    registerMigrations()
