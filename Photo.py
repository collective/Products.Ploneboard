import sys
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore import CMFCorePermissions 

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.CMFDefault.Image import Image
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
import OFS.Image
from Acquisition import aq_parent, aq_base

from cStringIO import StringIO

from BTrees.OOBTree import OOBTree

factory_type_information = {
    'id'             : 'Photo',
    'meta_type'      : 'Photo',
    'description'    : 'Photos objects can be embedded in Portal documents.',
    'icon'           : 'image_icon.gif',
    'product'        : 'CMFPhoto',
    'factory'        : 'addPhoto',
    'immediate_view' : 'metadata_edit_form',
    'actions'        :
    ( { 'id'            : 'view',
        'name'          : 'View',
        'action'        : '',
        'permissions'   : (CMFCorePermissions.View, )
        }, 
      { 'id'            : 'edit',
        'name'          : 'Properties',
        'action'        : 'portal_form/image_edit_form',
        'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
        },
      { 'id'            : 'metadata',
        'name'          : 'Metadata',
        'action'        : 'portal_form/metadata_edit_form',
        'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
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

    
    meta_type = 'Photo'


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


    displays = {'thumbnail': (128,128),
                'xsmall': (200,200),
                'small': (320,320),
                'medium': (480,480),
                'large': (768,768),
                'xlarge': (1024,1024)
                }


    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE, size=None):
        """Return the image data."""
        if size in self.displays.keys():
            # Create resized copy, if it doesnt already exist
            if not self._photos.has_key(size):
                resolution = self.displays.get(size, (0,0))
                raw = str(self.data)
                image = OFS.Image.Image(size, size, self._resize(resolution))
                self._photos[size] = image
        
            return self._photos[size].index_html(REQUEST, RESPONSE)

        return Photo.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    def tag(self, size='original'):
        """ Return an HTML img tag """
        try:
            if size in self.displays.keys():
                # Create resized copy, if it doesnt already exist
                if not self._photos.has_key(size):
                    resolution = self.displays.get(size, (0,0))
                    raw = str(self.data)
                    image = OFS.Image.Image(size, size, self._resize(resolution))
                    self._photos[size] = image

            photo = self._photos[size]
        except KeyError:
            photo = self

        return '<img src="%s?size=%s" alt="%s" width="%s" height="%s" />' % (self.absolute_url(),
                                                                             size,
                                                                             self.title_or_id(),
                                                                             photo.width,
                                                                             photo.height)


    def _resize(self, size, quality=100):
        """Resize and resample photo."""
        image = StringIO()

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

        imgin.write(str(self.data))
        imgin.close()
        image.write(imgout.read())
        imgout.close()

        #Wait for process to close if unix. Should check returnvalue for wait
        if sys.platform !='win32':
            convert.wait()

        image.seek(0)
        return image


    security.declareProtected(CMFCorePermissions.View, 'get_exif')
    def get_exif(self):
        """
	Extracts the exif metadata from the image and returns
	it as a hashtable
	"""
        import EXIF

	try:
    	    data = EXIF.process_file(StringIO(self.data.data))
	except:
	    data = {}
	if not data:
	    data = {}

        keys = data.keys()
        keys.sort()

        result = {}

        for key in keys:
            if key in ('JPEGThumbnail', 'TIFFThumbnail'):
                continue
	    try:
		result[key] = str(data[key].printable)
	    except:
		pass
        return result


InitializeClass(Photo)

