"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based ATContentTypes (http://sf.net/projects/collective/).

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

$Id: ATCTMigrator.py,v 1.3 2004/03/16 15:27:10 tiran Exp $
"""

from common import *
from Walker import CatalogWalker
from Migrator import CMFItemMigrator, CMFFolderMigrator
from Products.CMFCore.utils import getToolByName

class DocumentMigrator(CMFItemMigrator):
    fromType = 'Document'
    toType   = 'ATDocument'
    # mapped in custom()
    # map = {'text' : 'setText'}
    
    def custom(self):
        mapping = {
                    'html' : 'text/html',
                    'structured-text': 'text/structured',
                    'plain' : 'text/plain',
                  }
        oldFormat = self.old.text_format
        newFormat = mapping.get(oldFormat, 'text/plain')
        oldText = self.old.text
        self.new.setText(oldText, mimetype = newFormat)

class EventMigrator(CMFItemMigrator):
    fromType = 'Event'
    toType   = 'ATEvent'
    map = {
            'location'      : 'setLocation',
            'Subject'       : 'setEventType',
            'event_url'     : 'setEventUrl',
            'start_date'    : 'setStartDate',
            'end_date'      : 'setEndDate',
            'contact_name'  : 'setContactName',
            'contact_email' : 'setContactEmail',
            'contact_phone' : 'setContactPhone',
          }

class FileMigrator(CMFItemMigrator):
    fromType = 'File'
    toType   = 'ATFile'
    # mapped in custom()
    # map = { 'file' : 'setFile' }

    def custom(self):
        ctype = self.old.getContentType()
        file = str(self.old)
        self.new.setFile(file, mimetype = ctype)

class ImageMigrator(CMFItemMigrator):
    fromType = 'Image'
    toType   = 'ATImage'
    # mapped in custom()
    # map = {'image':'setImage'}
    
    def custom(self):
        ctype = self.old.getContentType()
        # to retrieve the binary data
        # it is not sufficient to just use str(self.old)
        image = self.old.data
        self.new.setImage(image, mimetype = ctype)

class LinkMigrator(CMFItemMigrator):
    fromType = 'Link'
    toType   = 'ATLink'
    map = {'remote_url' : 'setRemoteUrl'}

class FavoriteMigrator(LinkMigrator):
    fromType = 'Favorite'
    toType   = 'ATFavorite'
    # see LinkMigrator
    # map = {'remote_url' : 'setRemoteUrl'}

class NewsItemMigrator(DocumentMigrator):
    fromType = 'News Item' 
    toType   = 'ATNewsItem'
    # see DocumentMigrator
    # map = {'text' : 'setText'}

class FolderMigrator(CMFFolderMigrator):
    fromType = 'Folder'
    toType   = 'ATFolder'
    # no other attributes to migrate
    map = {}

class LargeFolderMigrator(CMFFolderMigrator):
    fromType = 'Large Plone Folder'
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
