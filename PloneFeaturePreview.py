"""
                                                                           
                      GRUF3 Feature-preview stuff.                         
                                                                           
 This code shouldn't be here but allow people to preview advanced GRUF3    
 features (eg. flexible LDAP searching in 'sharing' tab, ...) in Plone 2,  
 without having to upgrade to Plone 2.1.
                                                                           
 Methods here are monkey-patched by now but will be provided directly by
 Plone 2.1.
 Please forgive this 'uglyness' but some users really want to have full    
 LDAP support without switching to the latest Plone version ! ;)


 BY DEFAULT, this thing is NOT enabled. To enable it, you have to do two
 things:

 * Install the gruf_plone_2_0 skin manually (see README file in this skin)

 * Put a 'preview.txt' file in your GroupUserFolder directory. Unless you
 do so, the monkeypatch won't be applied.


 This stuff is only provided for convenience and should be considered as
 experimental.
"""

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from GroupsToolPermissions import AddGroups
from GroupsToolPermissions import ManageGroups
from GroupsToolPermissions import DeleteGroups
from GroupsToolPermissions import ViewGroups
from GroupsToolPermissions import SetGroupOwnership
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from interfaces.portal_groups import portal_groups as IGroupsTool
from global_symbols import *



# This is "stollen" from MembershipTool.py
# this should probably be in MemberDataTool.py
def searchForMembers( self, REQUEST=None, **kw ):
    """
    searchForMembers(self, REQUEST=None, **kw) => normal or fast search method.

    The following properties can be provided:
    - name
    - email
    - last_login_time
    - roles

    This is an 'AND' request.

    If name is provided, then a _fast_ search is performed with GRUF's
    searchUsersByName() method. This will improve performance.

    In any other case, a regular (possibly _slow_) search is performed.
    As it uses the listMembers() method, which is itself based on gruf.getUsers(),
    this can return partial results. This may change in the future.
    """
    md = self.portal_memberdata
    mt = self.portal_membership
    if REQUEST:
        dict = REQUEST
    else:
        dict = kw

    # Attributes retreiving & mangling
    name = dict.get('name', None)
    email = dict.get('email', None)
    roles = dict.get('roles', None)
    last_login_time = dict.get('last_login_time', None)
    is_manager = mt.checkPermission('Manage portal', self)
    if name:
        name = name.strip().lower()
    if email:
        email = email.strip().lower()


    # We want 'name' request to be handled properly with large user folders.
    # So we have to check both the fullname and loginname, without scanning all
    # possible users.
    md_users = None
    uf_users = None
    if name:
        # We first find in MemberDataTool users whose _full_ name match what we want.
        lst = md.searchMemberDataContents('fullname', name)
        md_users = [ x['username'] for x in lst ]

        # Fast search management if the underlying acl_users support it.
        # This will allow us to retreive users by their _id_ (not name).
        acl_users = self.acl_users
        meth = getattr(acl_users, "searchUsersByName", None)
        if meth:
            uf_users = meth(name)           # gruf search

    # Now we have to merge both lists to get a nice users set.
    # This is possible only if both lists are filled (or we may miss users else).
    Log(LOG_DEBUG, md_users, uf_users, )
    members = []
    if md_users is not None and uf_users is not None:
        names_checked = 1
        wrap = mt.wrapUser
        getUser = acl_users.getUser
        for userid in md_users:
            members.append(wrap(getUser(userid)))
        for userid in uf_users:
            if userid in md_users:
                continue             # Kill dupes
            members.append(wrap(getUser(userid)))

        # Optimization trick
        if not email and \
               not roles and \
               not last_login_time:
            return members          
    else:
        # If the lists are not available, we just stupidly get the members list
        members = self.listMembers()
        names_checked = 0

    # Now perform individual checks on each user
    res = []
    portal = self.portal_url.getPortalObject()

    for member in members:
        #user = md.wrapUser(u)
        u = member.getUser()
        if not (member.listed or is_manager):
            continue
        if name and not names_checked:
            if (u.getUserName().lower().find(name) == -1 and
                member.getProperty('fullname').lower().find(name) == -1):
                continue
        if email:
            if member.getProperty('email').lower().find(email) == -1:
                continue
        if roles:
            user_roles = member.getRoles()
            found = 0
            for r in roles:
                if r in user_roles:
                    found = 1
                    break
            if not found:
                continue
        if last_login_time:
            if member.last_login_time < last_login_time:
                continue
        res.append(member)
    Log(LOG_DEBUG, res)
    return res


def listAllowedMembers(self,):
    """listAllowedMembers => list only members which belong
    to the same groups/roles as the calling user.
    """
    user = self.REQUEST['AUTHENTICATED_USER']
    caller_roles = user.getRoles()              # Have to provide a hook for admins
    current_members = self.listMembers()
    allowed_members =[]
    for member in current_members:
        for role in caller_roles:
            if role in member.getRoles():
                allowed_members.append(member)
                break
    return allowed_members


# Monkeypatch it !
if PREVIEW_PLONE21_IN_PLONE20_:
    from Products.CMFPlone import MembershipTool
    MembershipTool.MembershipTool.searchForMembers = searchForMembers
    MembershipTool.MembershipTool.listAllowedMembers = listAllowedMembers
    Log(LOG_NOTICE, "Applied GRUF's monkeypatch over Plone 2. Please remember this feature is experimental.")



