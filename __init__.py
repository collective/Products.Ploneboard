import sys
import CMFPhotoFolder
import CMFPhoto
from Products.CMFCore import utils, DirectoryView

ADD_CONTENT_PERMISSION = 'Add portal content' # disgusting isn't it ?

bases = (CMFPhotoFolder.CMFPhotoFolder, CMFPhoto.CMFPhoto)

this_module = sys.modules[__name__]
z_bases = utils.initializeBasesPhase1(bases, this_module)

photo_globals = globals()

DirectoryView.registerDirectory('skins', globals())

def initialize(registrar):
    utils.initializeBasesPhase2(z_bases, registrar)
    utils.ContentInit(
        'CMFPhoto',
        content_types = bases,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = (CMFPhotoFolder.addCMFPhotoFolder, CMFPhoto.addCMFPhoto),
        fti = (CMFPhotoFolder.factory_type_information, CMFPhoto.factory_type_information),
        ).initialize(registrar)

