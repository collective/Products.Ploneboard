"""
 Install by adding an external method which calls 'purgePhotoCache'
 Manually purge the photo cache.

 Useful if you are playing around with dispaly size settings.

"""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.debug import log, log_exc

from BTrees.OOBTree import OOBTree


def getAllPhotos(self):
    catalog = getToolByName(self, 'portal_catalog')
    results = catalog(Type = 'Photo')
    #log (results)
    results = [r.getObject() for r in results]
    return results

def purgePhotoCache(self):
    """ To be called by an External Method"""
    for photo in getAllPhotos(self):
        log("deleting %s's photo cache" % photo.Title())
        photo._photos = OOBTree()
        
    return "Photo Cache Purged"
