import sys
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore import CMFCorePermissions 

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.CMFDefault.Image import Image

import OFS.Image

from cStringIO import StringIO

from BTrees.OOBTree import OOBTree

factory_type_information = {
    'id'             : 'Photo'
    , 'meta_type'      : 'Portal Photo'
    , 'description'    : 'Photos objects can be embedded in Portal documents.'
    , 'icon'           : 'image_icon.gif'
    , 'product'        : 'CMFPhoto'
    , 'factory'        : 'addPhoto'
    , 'immediate_view' : 'metadata_edit_form'
    , 'actions'        :
    ( { 'id'            : 'view'
        , 'name'          : 'View'
        , 'action'        : 'photo_view'
        , 'permissions'   : (CMFCorePermissions.View, )
        }
       ,{ 'id'            : 'settings' 
          , 'name'          : 'Settings'
          , 'action'        : 'portal_form/photo_settings_form'
          , 'permissions'   :
          (CMFCorePermissions.View,)
          , 'category'      : 'object'
          }
      , { 'id'            : 'rotate'
          , 'name'          : 'Rotate'
          , 'action'        : 'portal_form/photo_rotate_form'
          , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
          }
      , { 'id'            : 'edit'
          , 'name'          : 'Edit'
          , 'action'        : 'portal_form/image_edit_form'
          , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
          }
      , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'action'        : 'portal_form/metadata_edit_form'
          , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
          }
      )
    }


def addPhoto( self
              , id
              , title=''
              , file=''
              , content_type=''
              , precondition=''
              , subject=()
              , description=''
              , contributors=()
              , effective_date=None
              , expiration_date=None
              , format='image/png'
              , language=''
              , rights=''
              ):
    """
    Add an Photo
    """
    
    # cookId sets the id and title if they are not explicity specified
    id, title = OFS.Image.cookId(id, title, file)
    
    self=self.this()

    # Instantiate the object and set its description.
    iobj = Photo( id, title, '', content_type, precondition, subject
                  , description, contributors, effective_date, expiration_date
                  , format, language, rights
                  )
    
    # Add the Photo instance to self
    self._setObject(id, iobj)

    # 'Upload' the photo.  This is done now rather than in the
    # constructor because it's faster (see File.py.)
    self._getOb(id).manage_upload(file)


class Photo(Image):
    """
    Implements a Photo, a scalable image
    """

    __implements__ = ( Image.__implements__ ,)
    
    meta_type = 'Portal Photo'

    displays = {'thumbnail': (128,128),
                'xsmall': (200,200),
                'small': (320,320),
                'medium': (480,480),
                'large': (768,768),
                'xlarge': (1024,1024)
                }

    def __init__( self
                , id
                , title=''
                , file=''
                , content_type=''
                , precondition=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='image/png'
                , language='en-US'
                , rights=''
                ):
        Image.__init__(self, id, title, file, content_type, precondition, 
                       subject, description, contributors, effective_date,
                       expiration_date, format, language, rights)

        self._photos = OOBTree()
    
    security = ClassSecurityInfo()


    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        Display the image
        """
        size = REQUEST.get('display', '')
        if size in self.displays.keys():
            if not size in self._photos.keys():
                self._photos[size] = OFS.Image.Image('Image', 'Image',
                                                     self._resize(self.displays.get(size, (0, 0))))
            return self._photos.get(size).index_html(REQUEST, RESPONSE)

        return OFS.Image.Image.index_html(self, REQUEST, RESPONSE)


    __call__ = index_html


    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        """Get the size of a file or image.

        Returns the size of the file or image.
        """
        size = self.REQUEST.get('display', '')
        photo = self._photos.get(size)
        if photo:
            return photo.get_size()
        else:
            return 'N/A'
        
        return Image.get_size(self)


    security.declareProtected(CMFCorePermissions.View, 'getDisplays')
    def getDisplays(self):
        result = []

        for name, size in self.displays.items():
            result.append({'name':name, 'label':'%s (%dx%d)' % (name, size[0], size[1])})

        return result
    

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'rotate')
    def rotate(self, degrees=0):
        """Rotate photo"""
        image = StringIO()
        
        if sys.platform == 'win32':
            from win32pipe import popen2
            imgin, imgout = popen2('convert -rotate %s - -'
                               % (degrees,), 'b')
        else:
            from popen2 import popen2
            imgout, imgin = popen2('convert -rotate %s - -'
                               % (degrees,))

        imgin.write(str(self.data))
        imgin.close()
        image.write(imgout.read())
        imgout.close()
        
        image.seek(0)
        self.manage_upload(image)
        self._photos = OOBTree()

        
    def _resize(self, size, quality=100):
        """Resize and resample photo."""
        image = StringIO()

        width, height = size
        
        if sys.platform == 'win32':
            from win32pipe import popen2
            imgin, imgout = popen2('convert -quality %s -geometry %sx%s - -'
                                   % (quality, width, height), 'b')
        else:
            from popen2 import popen2
            imgout, imgin = popen2('convert -quality %s -geometry %sx%s - -'
                                   % (quality, width, height))

        imgin.write(str(self.data))
        imgin.close()
        image.write(imgout.read())
        imgout.close()
        image.seek(0)
        return image
    

InitializeClass(Photo)

