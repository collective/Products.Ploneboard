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


"""

from common import *
from Walker import CatalogWalker, CatalogWalkerWithLevel, StopWalking
from Migrator import CMFItemMigrator, CMFFolderMigrator
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Products.ATContentTypes.Extensions.toolbox import _fixLargePloneFolder

##def isPloneFolder(obj, ob=None):
##    if ob:
##        # called as instance method
##        obj = ob
##    # We can't use the type information because they are FU!
##    mtobj = getattr(obj, 'meta_type', None)
##    mtp   = getattr(aq_parent(obj), 'meta_type', None)
##    return mtobj == 'PloneFolder' and mtp != 'PloneFolder'
##
##def isPloneBTreeFolder(obj, ob=None):
##    if ob:
##        # called as instance method
##        obj = ob
##    # We can't use the type information because they are FU!
##    mtobj = getattr(obj, 'meta_type', None)
##    mtp   = getattr(aq_parent(obj), 'meta_type', None)
##    return mtobj == 'PloneBTreeFolder' and mtp != 'PloneBTreeFolder'


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
             ImageMigrator, LinkMigrator, NewsItemMigrator
            )

folderMigrators = ( FolderMigrator, LargeFolderMigrator)


def migrateAll(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    out = []
    out.append('Migration: ')
    for migrator in migrators:
        out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.fromType, migrator.toType))
        w = CatalogWalker(migrator, catalog)
        out+= w.go()
    for migrator in folderMigrators:
        out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.fromType, migrator.toType))
        while 1:
            # loop around until we got 'em all :]
            w = CatalogWalkerWithLevel(migrator, catalog, depth)
            try:
                o=w.go()
            except StopWalking:
                depth=2
                out.append(w.getOutput())
                break
            else:
                out.append(o)
                depth+=1

    wf = getToolByName(catalog, 'portal_workflow')
    LOG('starting wf migration')
    count = wf.updateRoleMappings()
    out.append('\n\n*** Workflow: %d object(s) updated. ***\n' % count)
    return '\n'.join(out)
