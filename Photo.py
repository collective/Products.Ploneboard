
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore import CMFCorePermissions

from Products.CMFDefault.Image import Image
import OFS.Image
from BTrees.OOBTree import OOBTree

from cgi import escape
from cStringIO import StringIO
import sys

factory_type_information = {
    'id'             : 'Photo',
    'meta_type'      : 'Photo',
    'description'    : 'Photos objects can be embedded in Portal documents.',
    'icon'           : 'image_icon.gif',
    'product'        : 'CMFPhoto',
    'factory'        : 'addPhoto',
    'immediate_view' : 'image_edit_form',
    'actions'        :
    ( { 'id'            : 'view',
        'name'          : 'View',
        'action'        : 'photo_view',
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

    def getPhoto(self,size):
        '''returns the Photo of the specified size'''
        return self._photos[size]

    security.declareProtected(CMFCorePermissions.View, 'getDisplays')
    def getDisplays(self):
        result = []

        for name, size in self.displays.items():
            result.append({'name':name, 'label':'%s (%dx%d)' % (name, size[0], size[1]),'size':size})

        result.sort(lambda d1,d2: cmp(d1['size'][0]*d1['size'][0],d2['size'][1]*d2['size'][1])) #sort ascending by size
        return result

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

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, title=None, size='original', **args):
        """ Return an HTML img tag (See OFS.Image)"""

        # Default values
        w=self.width
        h=self.height

        if height is None or width is None:

            if size in self.displays.keys():
                if not self._photos.has_key(size):
                    # This resized image isn't created yet.
                    # Calculate a size for it
                    x,y = self.displays.get(size)
                    try:
                        if self.width > self.height:
                            w=x
                            h=int(round(1.0/(float(self.width)/w/self.height)))
                        else:
                            h=y
                            w=int(round(1.0/(float(self.height)/x/self.width)))
                    except ValueError:
                        # OFS.Image only knows about png, jpeg and gif.
                        # Other images like bmp will not have height and
                        # width set, and will generate a ValueError here.
                        # Everything will work, but the image-tag will render 
                        # with height and width attributes.
                        w=None
                        h=None
                else:
                    # The resized image exist, get it's size
                    photo = self._photos.get(size)
                    w=photo.width
                    h=photo.height

        if height is None: height=h
        if width is None:  width=w

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale

        if xdelta and width:
            width =  str(int(round(int(width) * xdelta)))
        if ydelta and height:
            height = str(int(round(int(height) * ydelta)))

        result='<img src="%s?size=%s"' % (self.absolute_url(), escape(size))

        if alt is None:
            alt=getattr(self, 'title', '')
        result = '%s alt="%s"' % (result, escape(alt, 1))

        if title is None:
            title=getattr(self, 'title', '')
        result = '%s title="%s"' % (result, escape(title, 1))

        if height:
            result = '%s height="%s"' % (result, height)

        if width:
            result = '%s width="%s"' % (result, width)

        if not 'border' in [ x.lower() for x in  args.keys()]:
            result = '%s border="0"' % result

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key in args.keys():
            value = args.get(key)
            result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result

    security.declarePrivate('update_data')
    def update_data(self, data, content_type=None, size=None):
        """
        Update/upload image -> remove all copies
        """
        Image.update_data(self, data, content_type, size)
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


    security.declareProtected(CMFCorePermissions.View, 'getEXIF')
    def getEXIF(self):
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
