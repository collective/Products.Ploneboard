from Products.GroupUserFolder import groupuserfolder_globals
from Products.GroupUserFolder.GroupUserFolder import GroupUserFolder
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Acquisition import aq_base
from OFS.Folder import manage_addFolder

SKIN_NAME = "gruf"
_globals = globals()

def install_plone(self, out):
    pass

def install_subskin(self, out, skin_name=SKIN_NAME, globals=groupuserfolder_globals):
    print >>out, "  Installing subskin."
    skinstool=getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
        print >>out, "    Adding directory view for GRUF"
        addDirectoryViews(skinstool, 'skins', globals)

    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName) 
        path = [i.strip() for i in  path.split(',')]
        try:
            if skin_name not in path:
                path.insert(path.index('custom') +1, skin_name)
        except ValueError:
            if skin_name not in path:
                path.append(skin_name)  

        path = ','.join(path)
        skinstool.addSkinSelection( skinName, path)
    print >>out, "  Done installing subskin."

def walk(out, obj, operation):
    if obj.isPrincipiaFolderish:
        for content in obj.objectValues():
            walk(out, content, operation)
    operation(out, obj)


def migrate_user_folder(obj, out, ):
    """
    Move a user folder into a temporary folder, create a GroupUserFolder,
    and then move the old user folder into the Users portion of the GRUF.
    NOTE: You cant copy/paste between CMF and Zope folder.  *sigh*
    """
    id = obj.getId()
    if id == 'acl_users':
        if obj.__class__.__name__ == "GroupUserFolder":
            # Avoid already-created GRUFs
            print >>out, "    Do NOT migrate acl_users at %s, as it is already a GroupUserFolder" % ('/'.join( obj.getPhysicalPath() ), )
            return out.getvalue()
        
        print >>out, "    Migrating acl_users folder at %s to a GroupUserFolder" % ('/'.join( obj.getPhysicalPath() ), )
        container = obj.aq_parent
        
        # move the existing acl_users into a temporary folder
        #tempid = 'temp_acl_users_' + str( int(obj.ZopeTime()) )
        #manage_addFolder( container, tempid ) #dont use a CMF Folder
        tmp_users=container._getOb('acl_users')
        tmp_allow=container.__allow_groups__
       
        #del container.__allow_groups__ 
        #container._delOb('acl_users')
       
        if 'acl_users' in container.objectIds():
            container.manage_delObjects('acl_users')
            
        #temp_fld=container._getOb(tempid)
        #temp_fld.__allow_groups__ = aq_base(temp_grp)
        #temp_fld._setOb('acl_users', aq_base(temp_obj))

        #container[tempid].manage_pasteObjects( container.manage_cutObjects(id) )
        #get_transaction().commit(1) #put in _p_jar, muhahaha!
        
        # create a GRUF
        #import pdb; pdb.set_trace()
        container.manage_addProduct['GroupUserFolder'].manage_addGroupUserFolder()
        
        # move the old acl_users folder into the GRUF
        container.acl_users.Users.manage_delObjects( 'acl_users' )
        #clipboard = container[tempid].manage_cutObjects( 'acl_users' )
        #container.acl_users.Users.manage_pasteObjects( clipboard )
        #XXX Thanks to tres for knocking me over the head for being a dult
        container.acl_users.Users.__allow_groups__ = aq_base(tmp_allow)
        container.acl_users.Users._setOb('acl_users', aq_base(tmp_users))

        # clean up our temp folder, and then we are done
        #container.manage_delObjects( tempid )
        
    return out.getvalue()
    

def migrate_plone_site_to_gruf(self, out = None):
    if out is None:
        out = StringIO()
    print >>out, "  Attempting to migrate UserFolders to GroupUserFolders..."
    urltool=getToolByName(self, 'portal_url')
    plonesite = urltool.getPortalObject()
    ## We disable the 'walk' operation because if the acl_users object is deep inside
    ## the Plone site, that is a real problem. Furthermore, that may be because
    ## we're already digging an GRUF and have the risk to update a GRUF/User/acl_users
    ## object !
##    walk(out, plonesite, migrate_user_folder)
    for obj in plonesite.objectValues():
        migrate_user_folder(obj, out, )
    print >>out, "  Done Migrating UserFolders to GroupUserFolders."
    return out.getvalue()
    
def install(self):
    out = StringIO()
    print >>out, "Installing GroupUserFolder"

    install_subskin(self, out)
    install_plone(self, out)
    migrate_plone_site_to_gruf(self, out)

    print >>out, "Done."
    
    return out.getvalue()
