"""Migration tools for ATContentTypes

Migration system for the migration from CMFPloneTypes to ATContentTypes 

Copyright (c) 2004, Christian Heimes and contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, 
   this list of conditions and the following disclaimer in the documentation 
   and/or other materials provided with the distribution.
 * Neither the name of the author nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

$Id: CPTMigrator.py,v 1.2 2004/03/16 15:27:10 tiran Exp $
"""

from common import *
from Walker import CatalogWalker
from Migrator import CMFItemMigrator, CMFFolderMigrator
from Products.CMFCore.utils import getToolByName

class DocumentMigrator(CMFItemMigrator):
    fromType = 'PloneDocument'
    toType   = 'ATDocument'
    # XXX mime?
    # map = {'getRawText' : 'setText'}

    def custom(self):
        oldField = self.old.getField('text')
        oldFormat = oldField.getContentType(self.old)
        oldText = oldField.getRaw(self.old)
        self.new.setText(oldText, mimetype = oldFormat)

class EventMigrator(CMFItemMigrator):
    fromType = 'PloneEvent'
    toType   = 'ATEvent'
    map = {
            'getRawLocation'   : 'setLocation',
            'getRawSubject'    : 'setEventType',
            'getRawEventUrl'   : 'setEventUrl',
            'getRawStartDate'  : 'setStartDate',
            'getRawEndDate'    : 'setEndDate',
            'getRawContactName'  : 'setContactName',
            'getRawContactEmail' : 'setContactEmail',
            'getRawContactPhone' : 'setContactPhone',
          }

class FileMigrator(CMFItemMigrator):
    fromType = 'PloneFile'
    toType   = 'ATFile'
    # XXX mime?
    #map = { 'getFile' : 'setFile' }

    def custom(self):
        oldField = self.old.getField('file')
        oldFormat = oldField.getContentType(self.old)
        oldFile = oldField.getRaw(self.old)
        self.new.setFile(oldFile, mimetype = oldFormat)

class ImageMigrator(CMFItemMigrator):
    fromType = 'PloneImage'
    toType   = 'ATImage'
    # XXX mime?
    #map = {'getImage' : 'setImage'}

    def custom(self):
        oldField = self.old.getField('image')
        oldFormat = oldField.getContentType(self.old)
        oldImage = oldField.getRaw(self.old)
        self.new.setImage(oldImage, mimetype = oldFormat)

class LinkMigrator(CMFItemMigrator):
    fromType = 'PloneLink'
    toType   = 'ATLink'
    map = {'getRawRemoteUrl' : 'setRemoteUrl'}

class FavoriteMigrator(LinkMigrator):
    fromType = 'PloneFavorite'
    toType   = 'ATFavorite'
    map = {'getRawRemoteUrl' : 'setRemoteUrl'}

class NewsItemMigrator(DocumentMigrator):
    fromType = 'PloneNews Item' 
    toType   = 'ATNewsItem'
    # see DocumentMigrator
    # map = {'getRawText' : 'setText'}

class FolderMigrator(CMFFolderMigrator):
    fromType = 'PloneFolder'
    toType   = 'ATFolder'
    # no other attributes to migrate
    map = {}

class LargeFolderMigrator(CMFFolderMigrator):
    fromType = 'PloneBTreeFolder'
    toType   = 'ATBTreeFolder'
    # no other attributes to migrate
    map = {}

migrators = (DocumentMigrator, EventMigrator, FavoriteMigrator, FileMigrator,
             ImageMigrator, LinkMigrator, NewsItemMigrator, FolderMigrator,
             LargeFolderMigrator,
            )

def migrateAll(catalog):
    out = 'Migration: \n'
    for migrator in migrators:
        out+='\n *** Migrating %s to %s\n\n *** ' % (migrator.fromType, migrator.toType)
        w = CatalogWalker(migrator, catalog)
        out+= w.go()
    wf = getToolByName(catalog, 'portal_workflow')
    LOG('starting wf migration')
    count = wf.updateRoleMappings()
    out+='\n *** Workflow: %d object(s) updated. *** \n' % count
    return out
