
from Products.CMFDefault.SkinnedFolder import SkinnedFolder

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

factory_type_information = {
    'id'             : 'Photo Folder'
    , 'meta_type'      : 'Portal Photo Folder'
    , 'description'    : """\
    Skinned folders can define custom 'view' actions."""
    , 'icon'           : 'folder_icon.gif'
    , 'product'        : 'CMFPhoto'
    , 'factory'        : 'addPhotoFolder'
    , 'filter_content_types' : 0
    , 'immediate_view' : 'folder_edit_form'
    , 'actions'        :
    (  { 'id'            : 'edit'
         , 'name'          : 'Edit'
         , 'action'        : 'folder_edit_form'
         , 'permissions'   :
         (CMFCorePermissions.ManageProperties,)
         , 'category'      : 'folder'
         }
       ,{ 'id'            : 'view' 
          , 'name'          : 'View'
          , 'action'        : 'photofolder_view'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'object'
          }
       ,{ 'id'            : 'slideshow' 
          , 'name'          : 'Slideshow'
          , 'action'        : 'photofolder_slideshow_start'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'object'
          }
       ,{ 'id'            : 'settings' 
          , 'name'          : 'Settings'
          , 'action'        : 'photo_settings_form'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'object'
          }
       ,{ 'id'            : 'view' 
          , 'name'          : 'View'
          , 'action'        : 'photofolder_view'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'folder'
          }
       ,{ 'id'            : 'slideshow' 
          , 'name'          : 'Slideshow'
          , 'action'        : 'photofolder_slideshow_start'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'folder'
          }
       ,{ 'id'            : 'settings' 
          , 'name'          : 'Settings'
          , 'action'        : 'photofolder_settings_form'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'folder'
          }
       , { 'id'            : 'local_roles'
           , 'name'          : 'Local Roles'
           , 'action'        : 'folder_localrole_form'
           , 'permissions'   :
           (CMFCorePermissions.ManageProperties,)
           , 'category'      : 'folder'
           }
       )
    }

def addPhotoFolder( self, id, title='', description='', REQUEST=None ):
    """
    """
    sf = PhotoFolder( id, title )
    sf.description = description
    self._setObject( id, sf )
    sf = self._getOb( id )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )


class PhotoFolder(SkinnedFolder):
    """
    The Photo Folder is a folder full of photos :)
    """

    meta_type = 'Portal Photo Folder'

    security = ClassSecurityInfo()

InitializeClass(PhotoFolder)
