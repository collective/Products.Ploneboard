from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore.CMFCorePermissions import View, ManageProperties

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.Photo.PhotoFolder import PhotoFolder

from ZTUtils import Batch

def addCMFPhotoFolder(
    self,
    id,
    title='',
    store='Image',
    engine='ImageMagick',
    quality=75,
    pregen=0,
    timeout=0):
    """
    Add a Photo Folder
    """

    photofolder = CMFPhotoFolder(id, title, store, engine, quality, pregen, timeout)
    self._setObject(id, photofolder)

factory_type_information = {
    'id'             : 'Photo Folder',
    'meta_type'      : 'CMFPhotoFolder',
    'description'    :
    """A PhotoFolder has content and behaves like a folder.""",
    'icon'           : 'folder_icon.gif',
    'product'        : 'CMFPhoto',
    'factory'        : 'addCMFPhotoFolder',
    'filter_content_types' : 1,
    'allowed_content_types' : ('Photo',),
    'immediate_view' : 'folder_contents',
    'actions'        :
    ( { 'id'            : 'view',
        'name'          : 'View',
        'action'        : 'photo_folder_view',
        'permissions'   : (View,),
        'category'      : 'folder'
        },
      { 'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'folder_edit_form',
        'permissions'   : (ManageProperties,),
        'category'      : 'folder'
        },
      { 'id'            : 'localroles',
        'name'          : 'Local Roles',
        'action'        : 'folder_localrole_form',
        'permissions'   : (ManageProperties,),
        'category'      : 'folder'
        },
      { 'id'            : 'syndication',
        'name'          : 'Syndication',
        'action'        : 'synPropertiesForm',
        'permissions'   : (ManageProperties,),
        'category'      : 'folder'
        }
      )
    }

class CMFPhotoFolder(SkinnedFolder, PhotoFolder, DefaultDublinCoreImpl):
    """
    """

    meta_type = 'CMFPhotoFolder'
    portal_type = 'CMFPhotoFolder'

    security = ClassSecurityInfo()

    def __init__(self,
                 id,
                 title='',
                 store='Image',
                 engine='ImageMagick',
                 quality=75,
                 pregen=0,
                 timeout=0,
                 ):

        PhotoFolder.__init__(self, id, title, store, engine, quality, pregen, timeout)
        DefaultDublinCoreImpl.__init__(self)
        
        self.id = id
        self.title=title

    security.declarePublic('getGroupsOfN')
    def getGroupsOfN(self, at_a_time):
        b = Batch(self.listFolderContents('CMFPhoto'), at_a_time, orphan=0)
        batches = [b]
        while b.next:
            b = b.next
            batches.append(b)

        return batches

    security.declareProtected('Access contents information', 'nextAlbum')
    def nextAlbum(self):
        """Return next PhotoFolder in folder."""
        id = self.getId()
        albumIds = self.aq_parent.contentIds(spec='CMFPhotoFolder')
        if id == albumIds[-1]:
            return None
        return getattr(self.aq_parent, albumIds[albumIds.index(id)+1]).absolute_url()

    security.declareProtected('Access contents information', 'prevAlbum')
    def prevAlbum(self):
        """Return previous PhotoFolder in folder."""
        id = self.getId()
        albumIds = self.aq_parent.contentIds(spec='CMFPhotoFolder')
        if id == albumIds[0]:
            return None
        return getattr(self.aq_parent, albumIds[albumIds.index(id)-1]).absolute_url()
     
InitializeClass(CMFPhotoFolder)

