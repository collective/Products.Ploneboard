from AccessControl import getSecurityManager, ClassSecurityInfo, Unauthorized
from Acquisition import aq_base, aq_parent
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.portal_memberdata import portal_memberdata
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFTypes.BaseFolder import BaseFolder
from Products.CMFTypes.debug import log
from Products.CMFTypes import registerType


class MemberDataTool(UniqueObject, SimpleItem, BaseFolder):
    __implements__ = portal_memberdata

    security=ClassSecurityInfo()

    type = BaseFolder.type
    meta_type = "MemberDataTool"
    id = "portal_memberdata"

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'folder_contents',
        'permissions': (CMFCorePermissions.View,) 
        },)

    manage_options = BaseFolder.manage_options

    
    ##IMPL DETAILS
    def __init__(self):
        BaseFolder.__init__(self, self.id)
        
        self.members  = OOBTree() #user.getUserName -> Member
        self.typeName = "Member"  #The name used for the factory in
                                  #types_tool

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self, 'view', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
             return view()



    def getMemberFactory(self):
        """return a callable that is the registered object returning a
        contentish member object"""
        # Assumptions: there is a types_tool type called Member, you
        # want one of these in the folder, changing this changes the
        # types of members in your site.
        types_tool = getToolByName(self, "portal_types")
        ti = types_tool.getTypeInfo(self.typeName)
        
        p = self.manage_addProduct[ti.product]
        action = getattr(p, ti.factory, None)
        if action is None: raise ValueError, ('Invalid Factory for %s'
                                              % ti.getId())
        return action


    def _deleteMember(self, id):
        """remove a member"""
        del self.members[id]
        
    
    ##PORTAL_MEMBERDATA INTERFACE IMPL
    def wrapUser(self, user):
        '''
        If possible, returns the Member object that corresponds
        to the given User object.
        '''
        name = user.getUserName()
        m = self.members.get(name)
        if not m:
            ## XXX Delegate to the factory and create a new site specific
            ## member object for this user
            m = self.getMemberFactory()(name)
            self.members[name] = m
        m.setUser(user)

        return m.__of__(self)

    def getMemberDataContents(self):
        '''
        Returns a list containing a dictionary with information 
        about the _members BTree contents: member_count is the 
        total number of member instances stored in the memberdata-
        tool while orphan_count is the number of member instances 
        that for one reason or another are no longer in the 
        underlying acl_users user folder.
        The result is designed to be iterated over in a dtml-in
        '''

        member_ids = [m.getUserName() for m in self.members.values()]
        user_ids = self.acl_users.getUserNames()
        oc = 0
        
        for id in member_ids:
            if id not in user_ids: oc += 1
                
        return [{
            'member_count' : len(member_ids),
            'orphan_count' : oc
            }]

    def pruneMemberDataContents():
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users

        The impl can override the pruneOrphan(id) method to do things
        like manage its workflow state. The default impl will remove.
        '''
        
        member_ids = [m.getUserName() for m in self.members.values()]
        user_ids = self.acl_users.getUserNames()

        for id in members_ids:
            if id not in user_ids:
                self.pruneOrphan(id)
                

    ## Folderish Methods
    def allowedContentTypes(self):
        ## XXX we want anything that is a subclass of Member?
        ## XXX or define a real registration mechinism, same for
        ## XXX all_meta_types
        tt = getToolByName(self, 'portal_types')
        ti = tt.getTypeInfo('Member')
        return [ti]

    security.declareProtected(CMFCorePermissions.ListPortalMembers, 'contentValues')
    def contentValues(self, spec=None, filter=None):
        objects = [v.__of__(self) for v in self.members.values()]
        l = []
        for v in objects:
            id = v.getId()
            try:
                if getSecurityManager().validate(self, self, id, v):
                    l.append(v)
            except Unauthorized:
                pass
        return l

    def _getUserFromUserFolder(self, name):
        return self.acl_users.getUser(name).__of__(self.acl_users)
       
   
    def __getattr__(self, id):
        if self.members.has_key(id):
            return self.members[id].__of__(self)
        
        return getattr(aq_parent(self), id)


    ##SUBCLASS HOOKS
    def pruneOrphan(self, id):
        """Called when a member object exists for something not in the
        acl_users folder
        """
        self._deleteMember(id)


from Products.CMFCore.utils import _verifyActionPermissions

def _getViewFor(obj, view='view', default=None):
    ti = obj.getTypeInfo()
    if ti is not None:
        actions = ti.getActions()
        for action in actions:
            if action.get('id', None) == default:
                default=action
            if action.get('id', None) == view:
                if _verifyActionPermissions(obj, action) and action['action']!='':
                    return obj.restrictedTraverse(action['action'])

        if default is not None:    
            if _verifyActionPermissions(obj, default):
                return obj.restrictedTraverse(default['action'])

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        #for action in actions:
        #    if _verifyActionPermissions(obj, action)  and action.get('action','')!='':
        #        return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(obj.getPhysicalPath()))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))


registerType(MemberDataTool)
