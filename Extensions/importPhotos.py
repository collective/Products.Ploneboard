"""
 Install by adding an external method which calls 'importAll'

 This script will recursivly import a directory structure into
 photo albums filled with photos.

"""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.debug import log, log_exc

import OFS.Image
import os

from Products.CMFPhoto import Photo

# the location of the photo hierarchy you wish to import 
PHOTO_DIRECTORY = '/home/zope/photos'

def importPhoto(args, dir, files):
    portal = args
    ##  change this variable to import your photos to a particular area on you site
    photoArea = portal

    folderTitle = dir[max(dir.rfind('/'),
                       dir.rfind('\\'),
                       dir.rfind(':'),
                       )+1:]
    folderId = folderTitle.replace(' ', '_')
    photoArea.invokeFactory(type_name='Photo Album', id=folderId, title=folderTitle)
    album = getattr(photoArea, folderId, None)

    for f in files:        
        full_filename = os.path.join(dir, f)

        if os.path.isdir(full_filename):
            return # no files in top level dir

        file = open(full_filename, 'r')
        log(full_filename)

        fileTitle = f 
        fileId = fileTitle.replace(' ', '_')
        #log("dirId=%s, dirTitle=%s, fileId=%s, filTitle=%s" % (folderId, folderTitle, fileId, fileTitle))
        
        album.invokeFactory(type_name='Photo', id=fileId, title=fileTitle, file=file, format='image/jpg')
        ob = getattr(album, id, None)
        log("added %s to %s" % (f, dir))

    return "uploaded %s" % full_filename

def importAll(self):
    """ To be called by an External Method"""
    os.path.walk(PHOTO_DIRECTORY, importPhoto, self)
