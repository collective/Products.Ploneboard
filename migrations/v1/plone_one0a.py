from Globals import package_home
import AccessControl
from Acquisition import aq_base
from Products.CMFPlone import MigrationTool
from Products.CMFMember import VERSION
import Products.CMFMember as CMFMember
import Products.CMFMember.MemberDataContainer as MemberDataContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from StringIO import StringIO
#from Products.CMFPlone.setup.ConfigurationMethods import modifyMembershipTool
#from Products.CMFMember.CatalogTool import CatalogTool
from Products.CMFMember.MembershipTool import MembershipTool


import os, types
from os.path import isdir, join

def _migrateTool(portal, toolid, name, attrs):
    orig=getToolByName(portal, toolid)
    portal.manage_delObjects(toolid)
    portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool(name)
    tool = getToolByName(portal, toolid)
    for attr in attrs:
        setattr(tool, attr, aq_base(getattr(aq_base(orig), attr)))
    return aq_base(orig)

def _getUserFolderForUser(portal, id=None):
    f = getToolByName(portal, 'portal_url').getPortalObject()
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


def _getUserById(portal, id):
    """A utility method for finding a user by searching through
    portal.acl_users as well as the acl_users folders for all
    zope folders containing portal.

    Returns the user in the acquisition context of its containing folder"""
    acl_users = _getUserFolderForUser(portal, id)
    if acl_users is None:
        return None
    return acl_users.getUser(id).__of__(acl_users)

def setupRegistration(portal): 
    out = []
    # restore Plone modifications after our install
    from Products.CMFPlone.setup.ConfigurationMethods import modifyMembershipTool
    modifyMembershipTool(portal, portal)
    
    # wire up join action to new machinery
    registration_tool=getToolByName(portal, 'portal_registration')
    actions=registration_tool._cloneActions()
    for action in actions:
        if action.id=='join':
            action.action=Expression('string:${portal_url}/createMember')
    registration_tool._actions=tuple(actions)
    out.append('Changed action for join')
    return out

def setupMembership(portal):
    out = []
    # Call the modifyMembershipTool from ConfigurationMethods in Plone
    #modifyMembershipTool(portal, getToolByName(portal, 'portal_url').getPortalObject())
    #out.write('Modified membership tool actions by calling modifyMembershipTool from Plone ConfigurationMethods')
    # wire up personalize action to new machinery
    pm = getToolByName(portal, 'portal_membership')
    actions = pm._cloneActions()
    res = []
    for a in actions:
        res.append( a.clone() )
    pm._actions = tuple(res)
    actions = res
    # plone_setup missing in old CMFMember
    setupLink = 1
    for action in actions:
        if action.id=='preferences':
            txt = action.action.text.replace('personalize_form', 'plone_memberprefs_panel')
            action.action = Expression(txt)
        if action.id=='plone_setup': setupLink = 0
    pm._actions = tuple(actions)
    out.append("Altered my preferences to point at the member preferences panel")

    # add in plone_setup to portal_membership if it is missing
    if setupLink:
        pm.addAction('plone_setup',
                     'Plone Setup',
                     'string: ${portal_url}/plone_control_panel',
                     '', # condition
                     CMFCorePermissions.ManagePortal,
                     'user',
                     1),
        out.append("Added missing Plone Setup action to membership tool")

    controlpanel=getToolByName(portal, 'portal_controlpanel')
    actions=controlpanel._cloneActions()
    for action in actions:
        if action.id=='MemberPrefs':
            action.action=Expression('string:${portal_url}/portal_memberdata/${portal/portal_membership/getAuthenticatedMember}/base_edit')
            out.append('Set the action url for member preferences')
    controlpanel._actions=tuple(actions)
    return out

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

def replaceTools(portal, custSchema, convert=1):
    out = []
    typestool=getToolByName(portal, 'portal_types')
    memberdata_tool = getToolByName(portal, 'portal_memberdata')
    portal = getToolByName(portal, 'portal_url').getPortalObject()
    if memberdata_tool.__class__ != CMFMember.MemberDataContainer.MemberDataContainer:
        membership_tool = getToolByName(portal, 'portal_membership')

        oldMemberData = {}
        for id in memberdata_tool._members.keys():
            user = _getUserById(portal, id)
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

        mdct = getattr(typestool, 'MemberDataContainer')
        mdct.global_allow = 1
        addTool = portal.manage_addProduct[CMFMember.PKG_NAME].manage_addTool
        portal.invokeFactory(id='portal_memberdata', type_name='MemberDataContainer')
        out.append('Added new portal_memberdata of type MemberDataContainer')

        memberdata_tool = portal.portal_memberdata
        memberdata_tool.setTitle('Member profiles')
        if custSchema:
            memberdata_tool.setMemberSchema(custSchema)

        mdct.global_allow = 0

#        if hasattr(portal, 'portal_registration'):
#            portal.manage_delObjects(['portal_registration'])
#        addTool('CMFMember Registration Tool', None)
#        out.append('Added CMFMember Registration tool')

        _migrateTool(portal, 'portal_registration',
                     'CMFMember Registration Tool',
                     ['_actions'])
        out.append('Migrated registration tool to CMFMember Registration tool')
#        _migrateTool(portal, 'portal_catalog',
#                     CatalogTool.meta_type,
#                     ['_actions', '_catalog'])
        out.append('Migrated catalog to Member Catalog tool')

        catalog = portal.portal_catalog
        catalog.addIndex('indexedUsersWithLocalRoles', 'KeywordIndex')
        catalog.addIndex('indexedOwner', 'FieldIndex')
        catalog.addColumn('indexedOwner')
        catalog.addColumn('indexedUsersWithLocalRoles')
        # XXX be sure to migrate portraits before replacing the membership tool
        ms_actions = []
        if hasattr(portal, 'portal_membership'):
            _migrateTool(portal, 'portal_membership',
                         MembershipTool.meta_type,
                         ['_actions'])
            out.append('Migrated membership tool to CMFMember Membership Tool')
        else:
            addTool('CMFMember Membership Tool', None)
            out.append('Added CMFMember Membership Tool')

        

        # Get the default member type from the control tool
        # Could be other types then default.
        memberdata_tool.setDefaultType(getToolByName(portal, 'cmfmember_control').getDefaultMemberType())
        
        # Get the factory for the default cmfmember type
        factory = MemberDataContainer.getMemberFactory(memberdata_tool, memberdata_tool.getTypeName())
        
        workflow_tool = getToolByName(portal, 'portal_workflow')
        users = ''
        for id in oldMemberData.keys():
            factory(id)
            new_member = memberdata_tool.get(id)
            new_member._migrate(oldMemberData[id], ['portrait'], out)

            try:
                workflow_tool.doActionFor(new_member, 'migrate') # put member in registered state without sending registration mail
            except:
                #No migrate transition in the workflow.
                pass
                
            # change ownership for migrated member
            new_member.changeOwnership(new_member.getUser(), 1)
            new_member.manage_setLocalRoles(new_member.getUserName(), ['Owner'])
            
            users += id + ', '
        out.append(users + ' migrated to ' + memberdata_tool.getTypeName())
        return out

def insertSkinsIntoSkinPath(portal):
    out = []
    skinstool = getToolByName(portal, 'portal_skins')
    globals = CMFMember.GLOBALS
    product_skins_dir = 'skins'
    fullProductSkinsPath = join(package_home(globals), product_skins_dir)
    files = os.listdir(fullProductSkinsPath)
    for productSkinName in files:
        if (isdir(join(fullProductSkinsPath, productSkinName))
            and productSkinName != 'CVS'
            and productSkinName != '.svn'):
            for skinName in skinstool.getSkinSelections():
                path = skinstool.getSkinPath(skinName)
                path = [i.strip() for i in  path.split(',')]
                try:
                    if productSkinName not in path:
                        path.insert(path.index('custom') +1, productSkinName)
                except ValueError:
                    if productSkinName not in path:
                        path.append(productSkinName)
                path = ','.join(path)
                skinstool.addSkinSelection(skinName, path)
    out.append("CMFMember skins inserted into skins path")
    return out

def updateVersionNumbers(portal):
    tool = getToolByName(portal, 'cmfmember_control')
    tool.setInstanceVersion(CMFMember.VERSION)
    memberdata_tool = portal.portal_memberdata
    memberdata_tool.setVersion(CMFMember.VERSION)

def migrateCustomMemberData(portal):
    out = []
    default_fields = ['email', 'portal_skin', 'listed', 'login_time',
                      'last_login_time', 'fullname', 'error_log_update',
                      'formtooltips', 'visible_ids', 'wysiwyg_editor']
    md_tool = portal.portal_memberdata
    a_m_d = actual_md_dict = md_tool.propdict()
    custom_fields = [md for md in actual_md_dict.keys() if md not in default_fields]
    from Products.CMFMember.utils import TYPESMAP as types_map

    select_types = ('selection', 'multiple selection')
    select_var_list = [a_m_d[prop]['select_variable'] \
                       for prop in a_m_d \
                       if a_m_d[prop]['type'] in select_types \
                       and a_m_d.has_key(a_m_d[prop]['select_variable']) ]

    select_vars = {}
    for select_var in select_var_list:
        select_vars[select_var] = md_tool.getProperty(select_var)

    cust_schema = ""
    for cust_field in custom_fields:
        if cust_field in select_vars:
            # we're making an assumption that if a property is
            # ever used as a select_variable, then we only want
            # to migrate it as a vocabulary and not as an actual
            # field in the schema
            continue
        prop = actual_md_dict[cust_field]
        prop_type = prop['type']
        field_type, widget_type = types_map[prop_type]

        prop_text = ""
        if prop_type in select_types:
            prop_sel_var = prop['select_variable']
            if prop_sel_var and (prop_sel_var in select_vars):
                for vocab_option in select_vars[prop_sel_var]:
                    prop_text += "   ('%s', '%s'),\n " % (vocab_option, vocab_option)
                prop_text = "vocabulary=DisplayList((%s)), \n" % prop_text

        widget_text = ""
        if widget_type:
            widget_text = "widget=%s(label='%s',)," % (widget_type, cust_field)

        default_text = ""
        prop_value = md_tool.getProperty(cust_field)
        if prop_value:
            # there's potentially a default value we need to capture
            if type(prop_value) in (types.StringType, types.UnicodeType):
                default_text = "default='%s', \n" % prop_value
            elif type(prop_value) in (types.IntType, types.LongType):
                default_text = "default='%d', \n" % prop_value
            elif type(prop_value) == types.FloatType:
                default_text = "default='%.9f', \n" % prop_value
            elif type(prop_value) == types.TupleType:
                default_text = "default='%s', \n" % str(prop_value).replace("'", '"')

        cust_schema += "%s('%s',\n %s%s%s),\n" % (field_type,
                                                  cust_field,
                                                  prop_text,
                                                  default_text,
                                                  widget_text,
                                                )
        out.append('Migrated custom field: %s' % cust_field)
    if custom_fields:
        cust_schema = "Schema((\n%s\n))" % cust_schema
    return out, cust_schema

def oneZeroAlpha(portal):
    """ Upgrade from default Plone Member to CMFMember 1.0 alpha"""
    out = []
    msgs, custSchema = migrateCustomMemberData(portal)
    for msg in msgs: out.append(msg)
    for msg in replaceTools(portal, custSchema): out.append(msg)
    for msg in setupMembership(portal): out.append(msg)
    for msg in setupRegistration(portal): out.append(msg)
    for msg in insertSkinsIntoSkinPath(portal): out.append(msg)
    updateVersionNumbers(portal)
    return out

if __name__=='__main__':
    registerMigrations()
