import sys
import Photo
from Products.CMFCore import utils, DirectoryView

ADD_CONTENT_PERMISSION = 'Add portal content' # disgusting isn't it ?

bases = (Photo.Photo, )

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
        extra_constructors = (Photo.addPhoto, ),
        fti = (Photo.factory_type_information, ),
        ).initialize(registrar)

