#################################################################################
#                                                                               #
#                       copyright (c) 2003 Ingeniweb SARL                       #
#                                                                               #
#################################################################################

"""GroupSpace main class"""


from Globals import InitializeClass
import string

from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents, AddPortalContent, ModifyPortalContent, AddPortalFolders
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore import CMFCorePermissions
from Products.CMFDefault import SkinnedFolder
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from OFS import Folder

from global_symbols import *


import os
import os.path
from Globals import package_home
DATA_PATH = os.path.join(package_home(globals()), 'data', 'groupspace_workflow.xml')


GroupSpace_editPermission = ModifyPortalContent
GroupSpace_addPermission = AddPortalFolders

# GroupSpace definition
factory_type_information = {
  'id'             : 'GroupSpace',
  'portal_type'    : 'GroupSpace',
  'meta_type'      : 'GroupSpace',
  'description'    : 'GroupSpaces can be used to create workgroup places for several site members.',
  'content_icon'   : 'GroupSpace.gif',                          # Icon has to be acquired from a skin folder
  'product'        : 'GroupUserFolder',
  'factory'        : 'addGroupSpace',
  'immediate_view' : 'GroupSpace_listing',                          
  'filter_content_types' : 0,                                   # This is for folderish types
  'allowed_content_types': (),                                  # If filter_content_types is true, this field can hold allowed meta_types
  'actions': (
    {
    'id'           : 'view',
    'name'         : 'View',
    'action'       : 'string:${folder_url}/GroupSpace_listing',
    'permissions'  : (CMFCorePermissions.View, ),
##    'category'      : 'folder',
    },
    {
    'id'            : 'folderlisting',
    'name'          : 'Contents',
    'action'        : 'string:${folder_url}/GroupSpace_contents',
    'permissions'   : (Permissions.access_contents_information,),
##    'category'      : 'folder',
    },
    {
    'id'            : 'groupspacemembers',
    'name'          : 'Members',
    'action'        : 'string:${folder_url}/GroupSpace_membersForm',
    'permissions'   : (Permissions.access_contents_information,),
##    'category'      : 'folder',
    },
    {
    'id'            : 'local_roles',
    'name'          : 'Sharing',
    'action'        : 'string:${folder_url}/folder_localrole_form',
    'permissions'   : (CMFCorePermissions.ManageProperties,),
##    'category'      : 'folder',
    },
    {
    'id'           : 'edit',
    'name'         : 'Properties',
    'action'       : 'string:${folder_url}/GroupSpace_editForm',
    'permissions'  : (GroupSpace_editPermission,),
##    'category'      : 'folder',
    },
  ),
  }

# The usual factory
def addGroupSpace(self, id, title = '', REQUEST = {}):
    """
    Factory method for a GroupSpace object
    """
    obj = GroupSpace(id, title)
    self._setObject(id, obj)

    Log(LOG_DEBUG, "Adding a new GroupSpace")
    usr_id = self.REQUEST.AUTHENTICATED_USER.getUserName()
    gs = getattr(self, id)
    gs.addGroupMember(usr_id)

    if REQUEST.has_key('RESPONSE'):
        return REQUEST.RESPONSE.redirect('manage_main')





class GroupSpace(SkinnedFolder.SkinnedFolder, ):
    """GroupSpace class"""
    meta_type = factory_type_information['meta_type']                   # Has not to be the same as FTI but it is the most usual case.

    manage_options = Folder.Folder.manage_options

    # Standard security settings
    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)            # $$$ Is this clever ? Isn't it better to make the object private ?


    # Init method
    def __init__(self, id, title=''):
        """__init__(self, id, title='')"""
        # NOTA : We shouldn't call parent's __init__ method as it would link to PortalFolder.__init__ and this
        # method sets 'self.id' and 'self.title' which is unuseful for us.
        self.id = id
        self.title = title


    # Edit method (change this to suit your needs)
    # This edit method should only change attributes that are neither 'id' or metadatas.
    security.declareProtected(GroupSpace_editPermission, 'manage_editGroupSpace')
    def manage_editGroupSpace(self, title = '', REQUEST = {}):
        """
        manage_editGroupSpace(self, title = '', REQUEST = {}) => object modification method
        """
        # Change title
        self.title = title
        if REQUEST is not None:
            return self.folder_contents(self, REQUEST, portal_status_message='Updated folder.')
        


    # This method comes from PloneFolder class.
    security.declareProtected(Permissions.access_contents_information, 'listFolderContents')
    def listFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ): 
        """
        Hook around 'contentValues' to let 'folder_contents'
        be protected.  Duplicating skip_unauthorized behavior of dtml-in.
        
        In the world of Plone we do not want to show objects that begin with a .
        So we have added a simply check.  We probably dont want to raise an
        Exception as much as we want to not show it.
        
        """

        items = self.contentValues(spec=spec, filter=contentFilter)
        l = []
        for obj in items:
            id = obj.getId()
            v = obj
            try:
                if suppressHiddenFiles and id[:1]=='.': 
                    raise Unauthorized(id, v)
                if getSecurityManager().validate(self, self, id, v):
                    l.append(obj)
            except (Unauthorized, 'Unauthorized'):
                pass
        return l



    #                                                                           #
    #                         GROUPSPACE-SPECIFIC METHODS                       #
    #                                                                           #

    # Security comments:
    #   GroupMembers adding / deletion is protected by the ManageProperties permission.
    #   Members listing is allowed upon AccessContentsInformation permission

    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "listGroupSpaceMemberUsers")
    def listGroupSpaceMemberUsers(self,):
        """
        listGroupSpaceMemberUsers(self,) => List actual members, by inspecting each group's members

        This can be very long on huge members lists
        """
        ret = []
        groups = []

        # Append pure users
        for id in self.listMemberIds():
            usr = self.acl_users.getUser(id)
            if not usr:
                # Not in this acl_users => add it directly
                ret.append(id)
            elif usr.isGroup():
                groups.append(id)
            else:
                ret.append(id)

        # Unmangle groups XXX has to be optimized !!!
        for group in groups:
            for usr in self.listUserIdsInGroup(group):
                if not usr in ret:
                    ret.append(usr)

        return ret
    

    security.declarePrivate("listUserIdsInGroup")
    def listUserIdsInGroup(self, group_id):
        """
        listUserIdsInGroup(self, group_id) => list of strings

        XXX can be optimized !
        """
        users=self.acl_users.getUsers()
        prefix=self.acl_users.getGroupPrefix()

        avail=[]
        for user in users:
            for group in user.getGroups():
                if group_id == group or \
                       prefix+group_id == group:
                    avail.append(user.getUserName())
        return avail


    security.declareProtected(CMFCorePermissions.ManageProperties, "addGroupMember")
    def addGroupMember(self, member_id):
        """
        addGroupMember(self, member_id) => Add a group member to this group space.

        This is done by granting him the GroupMember localrole on this folder.
        """
        # Check if it is a valid member id
        # XXX TODO

        # Add its local role
        self.manage_addLocalRoles(member_id, ["GroupMember",], )


    security.declareProtected(CMFCorePermissions.ManageProperties, "removeGroupMember")
    def removeGroupMember(self, member_id):
        """
        removeGroupMember(self, member_id) => Remove a group member to this group space

        """
        # Check if it is a valid member id
        # XXX TODO

        # Remove each and every local role which starts with "Group..."
        local_roles = self.get_local_roles_for_userid(member_id)
        new_lr = []
        for lr in local_roles:
            if not lr.startswith("Group"):
                new_lr.append(lr)
        if new_lr:
            self.manage_setLocalRoles(member_id, new_lr)
        else:
            self.manage_delLocalRoles([member_id])


    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "listMemberIds")
    def listMemberIds(self,):
        """
        listMemberIds(self,) => Return a list of member ids for this groupspace.
        This will return both users and groups.
        """
        ret = []
        
        # Add people with "Owner" & "GroupMember" local roles
        ret.extend(self.users_with_local_role("Owner"))
        ret.extend(self.users_with_local_role("GroupMember"))                # XXX This is NOT recursive,

        # flatten the list so that there's no double entries
        # XXX this code should be far better ! :)
        ret2 = []
        for item in ret:
            if not item in ret2:
                ret2.append(item)
        return ret2


    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "getMainOwner")
    def getMainOwner(self,):
        """
        getMainOwner(self,) => Return the main owner of the group space.
        It's likely that this will be the person in charge of maintaining it ! :-)
        """
        return self.listGroupOwners()[0]


    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "listGroupOwners")
    def listGroupOwners(self,):
        """
        listGroupOwners(self,) => Return a list of all persons having 'Owner' role in this group space.
        """
        ret = self.users_with_local_role("Owner")

        # XXX TODO:
        # XXX HAVE TO EXTEND THIS LIST TO ALL PEOPLE HAVING THE 'OWNER' ROLE,
        # XXX EVEN IF IT'S NOT A LOCAL ROLE !
        return ret

        


    #                                           #
    #           Various utilities               #
    #                                           #


    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "getGroupSpaceId")
    def getGroupSpaceId(self,):
        """
        getGroupSpaceId(self,) => Return groupspace's path
        """
        return string.join(self.getPhysicalPath(),'')

    security.declarePublic("canChange")
    def canChange(self,):
        """
        canChange(self,) => return true if the current user can change things in here
        """
        return self.REQUEST.AUTHENTICATED_USER.has_permission(CMFCorePermissions.ManageProperties, self)


    security.declareProtected(CMFCorePermissions.AccessContentsInformation, "listMembersForDisplay")
    def listMembersForDisplay(self,):
        """
        listMembersForDisplay(self,) => Same as listMemberIds() but with an accurate structure to
        display information.

        - Users are filtered
        - Roles are listed
        - Kind (user, group or unknown) is specified

        This method returns a list of tuples (massagedUsername, userType, actualUserName)
        """
        ret = []
        for usr_id in self.listMemberIds():
            obj = self.acl_users.getUser(usr_id)
            if not obj:
                # User not in the first acl_users
                ret.append((usr_id, "unknown", usr_id, ))
                continue
            if obj.isGroup():
                ret.append((obj.getUserNameWithoutGroupPrefix(), "group", usr_id, ))
            else:
                ret.append((obj.getUserName(), "user", usr_id, ))
        return ret



# Class instanciation
InitializeClass(GroupSpace)


