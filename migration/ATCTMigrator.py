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

$Id: ATCTMigrator.py,v 1.12 2004/08/09 07:44:09 tiran Exp $
"""

from common import *
from Walker import CatalogWalker, CatalogWalkerWithLevel, StopWalking
from Migrator import CMFItemMigrator, CMFFolderMigrator
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

from Products.ATContentTypes.types import ATDocument, ATEvent, \
    ATFavorite, ATFile, ATFolder, ATImage, ATLink, ATNewsItem
from Products.ATContentTypes.Extensions.toolbox import _fixLargePloneFolder

##def isPloneFolder(obj, ob=None):
##    if ob:
##        # called as instance method
##        obj = ob
##    # We can't use the type information because they are FU for the members folder!
##    mtobj = getattr(obj, 'meta_type', None)
##    mtp   = getattr(aq_parent(obj), 'meta_type', None)
##    return mtobj == 'Plone Folder' and mtp != 'Plone Folder'
##
##def isLargePloneFolder(obj, ob=None):
##    if ob:
##        # called as instance method
##        obj = ob
##    # We can't use the type information because they are FU for the members folder!
##    mtobj = getattr(obj, 'meta_type', None)
##    mtp   = getattr(aq_parent(obj), 'meta_type', None)
##    return mtobj == 'Large Plone Folder' and mtp != 'Large Plone Folder'


class DocumentMigrator(CMFItemMigrator):
    fromType = ATDocument.ATDocument.newTypeFor[0]
    toType   = ATDocument.ATDocument.__name__
    map = {'text' : 'setText'}

    def custom(self):
        oldFormat = self.old.text_format
        # ATDocument does automagically conversion :]
        self.new.setContentType(oldFormat)

class EventMigrator(CMFItemMigrator):
    fromType = ATEvent.ATEvent.newTypeFor[0]
    toType   = ATEvent.ATEvent.__name__
    map = {
            'location'      : 'setLocation',
            'Subject'       : 'setEventType',
            'event_url'     : 'setEventUrl',
            #'start_date'    : 'setStartDate',
            #'end_date'      : 'setEndDate',
            'contact_name'  : 'setContactName',
            'contact_email' : 'setContactEmail',
            'contact_phone' : 'setContactPhone',
          }

    def custom(self):
        sdate = self.old.start_date
        edate = self.old.end_date

        if sdate is None:
            sdate = self.old.created()
        if edate is None:
            edate = sdate

        self.new.setStartDate(sdate)
        self.new.setEndDate(edate)


class FileMigrator(CMFItemMigrator):
    fromType = ATFile.ATFile.newTypeFor[0]
    toType   = ATFile.ATFile.__name__
    # mapped in custom()
    # map = { 'file' : 'setFile' }

    def custom(self):
        ctype = self.old.getContentType()
        file = str(self.old)
        self.new.setFile(file, mimetype = ctype)

class ImageMigrator(CMFItemMigrator):
    fromType = ATImage.ATImage.newTypeFor[0]
    toType   = ATImage.ATImage.__name__
    # mapped in custom()
    # map = {'image':'setImage'}

    def custom(self):
        ctype = self.old.getContentType()
        # to retrieve the binary data
        # it is not sufficient to just use str(self.old)
        image = self.old.data
        self.new.setImage(image, mimetype = ctype)

class LinkMigrator(CMFItemMigrator):
    fromType = ATLink.ATLink.newTypeFor[0]
    toType   = ATLink.ATLink.__name__
    map = {'remote_url' : 'setRemoteUrl'}

class FavoriteMigrator(LinkMigrator):
    fromType = ATFavorite.ATFavorite.newTypeFor[0]
    toType   = ATFavorite.ATFavorite.__name__
    # see LinkMigrator
    # map = {'remote_url' : 'setRemoteUrl'}

class NewsItemMigrator(DocumentMigrator):
    fromType = ATNewsItem.ATNewsItem.newTypeFor[0]
    toType   = ATNewsItem.ATNewsItem.__name__
    # see DocumentMigrator
    map = {'text' : 'setText'}

class FolderMigrator(CMFFolderMigrator):
    fromType = ATFolder.ATFolder.newTypeFor[0]
    toType   = ATFolder.ATFolder.__name__
    # XXX checkMethod = isPloneFolder
    # no other attributes to migrate
    map = {}

class LargeFolderMigrator(CMFFolderMigrator):
    fromType = ATFolder.ATBTreeFolder.newTypeFor[0]
    toType   = ATFolder.ATBTreeFolder.__name__
    # no other attributes to migrate
    map = {}

migrators = (DocumentMigrator, EventMigrator, FavoriteMigrator, FileMigrator,
             ImageMigrator, LinkMigrator, NewsItemMigrator,
            )

folderMigrators = ( FolderMigrator, LargeFolderMigrator)

def migrateAll(portal):
    # first fix Members folder
    _fixLargePloneFolder(portal)
    catalog = getToolByName(portal, 'portal_catalog')
    out = []
    out.append('Migration: ')
    for migrator in migrators:
        out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.fromType, migrator.toType))
        w = CatalogWalker(migrator, catalog)
        out.append(w.go())
    for migrator in folderMigrators:
        out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.fromType, migrator.toType))
        depth=2
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
