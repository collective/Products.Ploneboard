from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Globals import InitializeClass
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base, BTreeFolder2
import OFS.Image
from cStringIO import StringIO
import sys
from zLOG import LOG, ERROR, WARNING
from Acquisition import aq_parent, aq_base, aq_self
from zExceptions import Unauthorized
from AccessControl import getSecurityManager

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
                                  }
                                )
                              }

class PhotoAlbum (BTreeFolder2Base, SkinnedFolder):
    meta_type = 'Photo Album'
    
    security=ClassSecurityInfo()

    def _checkId(self, id, allow_dup=0):
        SkinnedFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

    displays = {'thumbnail': (128,128),
                'xsmall': (200,200),
                'small': (320,320),
                'medium': (480,480),
                'large': (768,768),
                'xlarge': (1024,1024)
                }


    security.declareProtected(CMFCorePermissions.View, 'getDisplays')
    def getDisplays(self):
        result = []

        for name, size in self.displays.items():
            result.append({'name':name, 'label':'%s (%dx%d)' % (name, size[0], size[1])})

        return result

    
def addPhotoAlbum( self, id, title='', description='', REQUEST=None ):
    """ adds a Photo Album """
    sf = PhotoAlbum(id)
    sf.title=title
    sf.description=description
    self._setObject( id, sf )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(PhotoAlbum)
