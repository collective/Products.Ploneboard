
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore import CMFCorePermissions 

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.CMFDefault.Image import Image

import OFS.Image

from cStringIO import StringIO

from BTrees.OOBTree import OOBTree

factory_type_information = { 'id'             : 'Photo'
                             , 'meta_type'      : 'Portal Photo'
                             , 'description'    : """\
Photos objects can be embedded in Portal documents."""
                             , 'icon'           : 'image_icon.gif'
                             , 'product'        : 'CMFPhoto'
                             , 'factory'        : 'addPhoto'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'image_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'image_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
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
        Display the image, with or without standard_html_[header|footer],
        as appropriate.
        """
        #if REQUEST['PATH_INFO'][-10:] == 'index_html':
        #    return self.view(self, REQUEST)
        return OFS.Image.Image.index_html(self, REQUEST, RESPONSE)

    security.declareProtected(CMFCorePermissions.View, 'thumbnail')
    def thumbnail(self, REQUEST, RESPONSE):
        """
        Return a thumbnail representaion of the image
        """
        return OFS.Image.Image('test', 'test', self._resize(80, 80)).index_html(REQUEST, RESPONSE)

    def _resize(self, width, height, quality=75):
        """Resize and resample photo."""
        image = StringIO()

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

