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
from AccessControl import getSecurityManager()

factory_type_information =  { 'id'             : 'Photo Album',
                              'meta_type'      : 'Photo Album',
                              'description'    : """Photo Albums contain other albums or images..""",
                              'icon'           : 'folder_icon.gif',
                              'product'        : 'CMFPhotoAlbum',
                              'factory'        : 'addPhotoAlbum',
                              'filter_content_types' : 1,
                              'allowed_content_types' : ('Image', 'Photo Album'),
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

    displays = {'thumbnail': (128,128),
                'xsmall': (200,200),
                'small': (320,320),
                'medium': (480,480),
                'large': (768,768),
                'xlarge': (1024,1024)
                }

    
    def _checkId(self, id, allow_dup=0):
        SkinnedFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)


    def __init__(self, id):
        SkinnedFolder.__init__(self, id)
        BTreeFolder2Base.__init__(self, id)
        self._resized_photos = BTreeFolder2('Photos')

    security.declarePublic('getResizedImage')
    def getResizedImage(self, REQUEST=None):
        """ """
        # TODO: Need to do security checks here.
        # This method should act as a proxy for the "real" image.
        #image = REQUEST.get('image')
        #user = getSecurityManager.getUser()
        #if user.has_permission(CMFCorePermissions.View, image):
        return self._resized_photos.get(image).index_html(REQUEST, REQUEST.response)

        #raise Unauthorized

    def __before_publishing_traverse__(self, ob, REQUEST):
        # Get the traversal stack
        stack = REQUEST.get('TraversalRequestNameStack', [])

        try:
            # The first item in the stack should be the requested size
            size = stack[0]

            if size in self.displays.keys():
                # Compose the name used for storing resized copies
                name = stack[1]
                resized_name = '%s_%s' % (name, size)

                # Create resized copy, if it doesnt already exist
                if not resized_name in self._resized_photos.keys():
                    resolution = self.displays.get(size, (0,0))
                    raw = str(getattr(self, name).data)
                    image = OFS.Image.Image('Image', 'Image', self._resize(raw, resolution))
                    self._resized_photos._setObject(resized_name, image)

                REQUEST.set('image', resized_name)
                REQUEST.set('TraversalRequestNameStack', ['getResizedImage'])

        except IndexError:
            # This should never happen. Folder is being traversed,
            # but the travese stack is empty.
            pass

    
    def _resize(self, image, size, quality=100):
        """Resize and resample photo."""
        result = StringIO()

        width, height = size
        
        if sys.platform == 'win32':
            from win32pipe import popen2
            imgin, imgout = popen2('convert -quality %s -geometry %sx%s - -'
                                   % (quality, width, height), 'b')
        else:
            from popen2 import Popen3
            convert=Popen3('convert -quality %s -geometry %sx%s - -'
                                   % (quality, width, height))
            imgout=convert.fromchild
            imgin=convert.tochild

        imgin.write(image)
        imgin.close()
        result.write(imgout.read())
        imgout.close()

        # Wait for process to close if unix.
        # TODO: Should check returnvalue for wait
        if sys.platform !='win32':
            convert.wait()

        result.seek(0)
        return result


    def _delObject(self, id):
        """
        Remove the named object from the folder.
        """
        # Collect a list of all resized copies
        remove_list = []
        for resized in self._resized_photos.keys():
            if resized.startswith(id):
                remove_list.append(resized)

        # Then remove them
        for item in remove_list:
            try:
                self._resized_photos._delObject(item)
            except:
                LOG('CMFPhotoAlbum', ERROR, 'Failed to remove resized copy',
                    error = sys.exc_info())
                
        BTreeFolder2Base._delObject(self, id)


def addPhotoAlbum( self, id, title='', description='', REQUEST=None ):
    """ adds a Photo Album """
    sf = PhotoAlbum(id)
    sf.title=title
    sf.description=description
    self._setObject( id, sf )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(PhotoAlbum)
