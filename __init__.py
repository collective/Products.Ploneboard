import sys
import PhotoAlbum
from Products.CMFCore import utils, DirectoryView

ADD_CONTENT_PERMISSION = 'Add portal content' # disgusting isn't it ?

bases = (PhotoAlbum.PhotoAlbum, )

this_module = sys.modules[__name__]
z_bases = utils.initializeBasesPhase1(bases, this_module)

photoalbum_globals = globals()

DirectoryView.registerDirectory('skins', globals())

def initialize(registrar):
    utils.initializeBasesPhase2(z_bases, registrar)
    utils.ContentInit(
        'CMFPhotoAlbum',
        content_types = bases,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = (PhotoAlbum.addPhotoAlbum, ),
        fti = (PhotoAlbum.factory_type_information, ),
        ).initialize(registrar)

