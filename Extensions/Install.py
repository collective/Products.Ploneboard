from Products.GroupUserFolder import groupuserfolder_globals
from Products.GroupUserFolder.GroupUserFolder import GroupUserFolder
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

SKIN_NAME = "gruf"
_globals = globals()

def install_plone(self, out):
    pass

def install_subskin(self, out, skin_name=SKIN_NAME, globals=groupuserfolder_globals):
    skinstool=getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
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

def walk(out, obj, operation):
    if obj.isPrincipiaFolderish:
        for content in obj.objectValues():
            walk(out, content, operation)
    operation(out, obj)


def migrate_user_folder(out, obj):
    """
    Move a user folder into a temporary folder, create a GroupUserFolder,
    and then move the old user folder into the Users portion of the GRUF.
    """
    id = obj.getId()
    if id == 'acl_users' and not isinstance(obj, GroupUserFolder):
        print >>out, "Migrating acl_users folder at %s to a GroupUserFolder" % ('/'.join( obj.getPhysicalPath() ), )
        container = obj.aq_parent
        
        # move the existing acl_users into a temporary folder
        tempid = 'temp_acl_users_' + str( int(obj.ZopeTime()) )
        container.manage_addFolder( tempid )
        clipboard = container.manage_cutObjects( id )
        container[tempid].manage_pasteObjects( clipboard )
        
        # create a GRUF
        container.manage_addProduct['GroupUserFolder'].manage_addGroupUserFolder()
        container.acl_users.Users.manage_delObjects( 'acl_users' )
        
        # move the old acl_users folder into the GRUF
        clipboard = container[tempid].manage_cutObjects( 'acl_users' )
        container.acl_users.Users.manage_pasteObjects( clipboard )
        
        # clean up our temp folder, and then we are done
        container.manage_delObjects( tempid )
    

def migrate_plone_site_to_gruf(self):
    out = StringIO()
    print >>out, "Migrating UserFolders to GroupUserFolders."
    urltool=getToolByName(self, 'portal_url')
    plonesite = urltool.getPortalObject()
    walk(out, plonesite, migrate_user_folder)
    print >>out, "Done."
    return out.getvalue()
    
def install(self):
    out = StringIO()
    print >>out, "Installing GroupUserFolder"
    
    install_subskin(self, out)
    install_plone(self, out)

    print >>out, "Done."
    
    return out.getvalue()
