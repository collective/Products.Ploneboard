
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Acquisition import aq_base

factory_type_information =  { 'id'             : 'Photo Album',
                              'meta_type'      : 'Photo Album',
                              'description'    : """Photo Albums contain other albums or images..""",
                              'icon'           : 'folder_icon.gif',
                              'product'        : 'CMFPhotoAlbum',
                              'factory'        : 'addPhotoAlbum',
                              'filter_content_types' : 1,
                              'allowed_content_types' : ('Photo', 'Photo Album'),
                              'immediate_view' : 'photoalbum_view',
                              'actions'        :
                              ( { 'id'            : 'view',
                                  'name'          : 'View',
                                  'action'        : 'photoalbum_view',
                                  'permissions'   : (CMFCorePermissions.View,),
                                  'category'      : 'folder'},
                                { 'id'            : 'local_roles',
                                  'name'          : 'Local Roles',
                                  'action'        : 'folder_localrole_form',
                                  'permissions'   : (CMFCorePermissions.ManageProperties,),
                                  'category'      : 'folder'},
                                { 'id'            : 'edit',
                                  'name'          : 'Properties',
                                  'action'        : 'portal_form/folder_edit_form',
                                  'permissions'   : (CMFCorePermissions.ManageProperties,),
                                  'category'      : 'folder'
                                  },
                                { 'id'            : 'mkdir',
                                  'name'          : 'mkdir',
                                  'action'        : 'createPhotoAlbumInstance',
                                  'permissions'   : (CMFCorePermissions.AddPortalContent,),
                                  'category'      : 'folder',
                                  'visible'       : 0
                                  }
                                )
                              }

class PhotoAlbum (BTreeFolder2Base, SkinnedFolder):
    meta_type = 'Photo Album'
    
    security=ClassSecurityInfo()

    def _checkId(self, id, allow_dup=0):
        SkinnedFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)


    security.declarePrivate('PUT_factory')
    def PUT_factory( self, name, typ, body ):
        """
        Dispatcher for PUT requests to non-existent IDs.
        PhotoAlbums should always use photos for images.
        """
        if typ.startswith('image'):
            self.invokeFactory( 'Photo', name )

            # XXX: this is butt-ugly.
            obj = aq_base( self._getOb( name ) )
            self._delObject( name )
            return obj

    
def addPhotoAlbum( self, id, title='', description='', REQUEST=None ):
    """ adds a Photo Album """
    sf = PhotoAlbum(id)
    sf.title=title
    sf.description=description
    self._setObject( id, sf )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(PhotoAlbum)
