
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ModifyPortalContent

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.Photo.Photo import Photo

def addCMFPhoto(
    self,
    id,
    title='',
    file='',
    store='Image',
    engine='ImageMagick',
    quality=75,
    pregen=0,
    timeout=0):
    """
    Add a Photo
    """

    photo = CMFPhoto(id, title, file, store, engine, quality, pregen, timeout)
    photo._data = ''
    self._setObject(id, photo)
    
factory_type_information = {
    'id'             : 'Photo',
    'meta_type'      : 'CMFPhoto',
    'description'    : 'A Photo.',
    'icon'           : 'image_icon.gif',
    'product'        : 'CMFPhoto',
    'factory'        : 'addCMFPhoto',
    'filter_content_types' : 0,
    'immediate_view' : 'metadata_edit_form',
    'actions'        :
    ( { 'id'            : 'view',
        'name'          : 'View',
        'action'        : 'photo_view',
        'permissions'   : (View, )
        },
      { 'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'image_edit_form',
        'permissions'   : (ModifyPortalContent, )
        },
      { 'id'            : 'metadata',
        'name'          : 'Metadata',
        'action'        : 'metadata_edit_form',
        'permissions'   : (ModifyPortalContent, )
        }
      )
    }

class CMFPhoto(Photo, PortalContent, DefaultDublinCoreImpl):
    """
    """

    meta_type = 'CMFPhoto'
    portal_type = 'CMFPhoto'

    def __init__(self,
                 id,
                 title='',
                 file='',
                 store='Image',
                 engine='ImageMagick',
                 quality=75,
                 pregen=0,
                 timeout=0,
                 ):

        Photo.__init__(self, id=id, title=title, file=file, store=store, engine=engine, quality=quality, pregen=pregen, timeout=timeout)
        DefaultDublinCoreImpl.__init__(self)
        
        self.id = id
        self.title=title
        
    security = ClassSecurityInfo()

    def SearchableText(self):
        """
        SeachableText is used for full text seraches of a portal.
        It should return a concatanation of all useful text.
        """

        return "%s %s" % (self.title, self.description)
            
    def manage_afterClone(self, item):
        """Both of my parents have an afterClone method"""
        Photo.manage_afterClone(self,item)
        PortalContent.manage_afterClone(self,item)

    def manage_afterAdd(self, item, container):
        """Both of my parents have an afterAdd method"""
        Photo.manage_afterAdd(self,item,container)
        PortalContent.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
        """Both of my parents have a beforeDelete method"""
        PortalContent.manage_beforeDelete(self, item, container)
        Photo.manage_afterAdd(self,item,container)

    security.declareProtected('Access contents information', 'nextPhoto')
    def nextPhoto(self):
        """Return next Photo in folder."""
        id = self.getId()
        photoIds = self.aq_parent.contentIds(spec='CMFPhoto')
        if id == photoIds[-1]:
            return None
        return getattr(self.aq_parent, photoIds[photoIds.index(id)+1]).absolute_url()

    security.declareProtected('Access contents information', 'prevPhoto')
    def prevPhoto(self):
        """Return previous Photo in folder."""
        id = self.getId()
        photoIds = self.aq_parent.contentIds(spec='CMFPhoto')
        if id == photoIds[0]:
            return None
        return getattr(self.aq_parent, photoIds[photoIds.index(id)-1]).absolute_url()

    security.declareProtected('Access contents information', 'tag')
    def tag(self, display=None, height=None, width=None, cookie=0,
            alt=None, css_class=None, **kw):
        """Return HTML img tag."""
        try:
            return Photo.tag(self, display, height, width, cookie, alt, css_class)
        except:
            return '%s is broken!' % self.title_or_id()

InitializeClass(CMFPhoto)

