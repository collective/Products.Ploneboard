"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

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

$Id: Migrator.py,v 1.8 2004/03/16 20:33:23 tiran Exp $
"""

from copy import copy, deepcopy

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_parent
from DateTime import DateTime
from Persistence import PersistentMapping

from common import *

fieldList = [
    # (accessor, mutator, field),
    ('Title', 'setTitle',                    ''),
    ('Creator', '',                          ''),
    ('Subject','setSubject',                 'subject'),
    ('Description','setDescription',         'description'),
    ('Publisher', '',                        ''),
    ('Contributors','setContributors',       'contributors'),
    ('Date', '',                             ''),
    ('CreationDate', '',                     ''),
    ('EffectiveDate','setEffectiveDate',     'effectiveDate'),
    ('ExpirationDate','setExpirationDate',   'expirationDate'),
    ('ModificationDate', '',                 ''),
    ('Type', '',                             ''),
    ('Format', 'setFormat',                  ''),
    ('Identifier', '',                       ''),
    ('Language','setLanguage',               'language'),
    ('Rights','setRights',                   'rights'),

    # allowDiscussion is not part of the official DC metadata set
    #('allowDiscussion','isDiscussable','allowDiscussion'),
  ]

metadataList = []
for accessor, mutator, field in fieldList:
    if accessor and mutator:
        metadataList.append((accessor, mutator))


    
def copyPermMap(old):
    """bullet proof copy
    """
    new = PersistentMapping()
    for k,v in old.items():
        nk = copy(k)
        nv = copy(v)
        new[k] = v
    return new

    
class BaseMigrator:
    """Migrates an object to the new type
    
    Base class
    """
    fromType = ''
    toType   = ''
    map      = {}

    subtransaction = 30

    def __init__(self, obj):
        self.old = obj
        self.orig_id = self.old.getId()

        self.old_id = '%s_MIGRATION_' % self.orig_id
        
        self.new = None
        self.new_id = self.orig_id
        
        self.parent = aq_parent(self.old)
        
        # safe id generation
        while hasattr(aq_base(self.parent), self.old_id):
            self.old_id+='X'

    def getMigrationMethods(self):
        """
        """
        methods     = []
        lastmethods = []
        for name in dir(self):
            if name.startswith('migrate_'):
                method = getattr(self, name)
                if callable(method):
                    methods.append(method)
            if name.startswith('last_migrate_'):
                method = getattr(self, name)
                if callable(method):
                    lastmethods.append(method)
        return methods+[self.custom]+lastmethods
        
    def migrate(self, unittest=0):
        """Migrates the object
        """
        self.renameOld()
        self.createNew()

        for method in self.getMigrationMethods():
            __traceback_info__ = (self, method, self.old, self.orig_id)
            # may raise an exception, catch it later
            method()

        self.remove()

    __call__ = migrate

    def renameOld(self):
        """Renames the old object

        Must be implemented by the real Migrator
        """
        raise NotImplementedError

    def createNew(self):
        """Create the new object
        
        Must be implemented by the real Migrator
        """
        raise NotImplementedError

    def custom(self):
        """For custom migration
        """
        pass
    
    def migrate_properties(self):
        """Migrates zope properties
        
        Removes the old (if exists) and adds a new
        """
        if not hasattr(aq_base(self.old), 'propertyIds') or \
          not hasattr(aq_base(self.new), '_delProperty'):
            # no properties available
            return None

        for id in self.old.propertyIds():
            LOG("propertyid: " + str(id))
            if id in ('title', 'description'):
                # migrated by dc
                continue
            if id in ('content_type', ):
                # has to be taken care of separately
                LOG("property with id: %s not migrated" % str(id))
                continue
            value = self.old.getProperty(id)
            type = self.old.getPropertyType(id)
            LOG("value: " + str(value) + "; type: " + str(type))
            if self.new.hasProperty(id):
                self.new._delProperty(id)
            LOG("property: " + str(self.new.getProperty(id)))
            self.new.manage_addProperty(id, value, type)

    def migrate_owner(self):
        """Migrates the zope owner
        """
        # getWrappedOwner is not always available
        if hasattr(self.old, 'getWrappedOwner'):
            owner = self.old.getWrappedOwner()
            self.new.changeOwnership(owner)
            LOG("changing owner via changeOwnership: %s" % str(self.old.getWrappedOwner()))
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            LOG("changing owner via property _owner: %s" % str(self.old.getOwner(info = 1)))
            self.new._owner = self.old.getOwner(info = 1)
    
    def migrate_withmap(self):
        """Migrates other attributes from obj.__dict__ using a map
        
        The map can contain both attribute names and method names
        
        'oldattr' : 'newattr'
            new.newattr = oldattr
        'oldattr' : ''
            new.oldattr = oldattr
        'oldmethod' : 'newattr'
            new.newattr = oldmethod()
        'oldattr' : 'newmethod'
            new.newmethod(oldatt)
        'oldmethod' : 'newmethod'
            new.newmethod(oldmethod())
        """
        for oldKey, newKey in self.map.items():
            LOG("oldKey: " + str(oldKey) + ", newKey: " + str(newKey))
            if not newKey:
                newKey = oldKey
            oldVal = getattr(self.old, oldKey)
            newVal = getattr(self.new, newKey)
            if callable(oldVal):
                value = oldVal()
            else:
                value = oldVal
            if callable(newVal):
                newVal(value)
            else:
                setattr(self.new, newKey, value)

    def remove(self):
        """Removes the old item

        Must be implemented by the real Migrator
        """
        raise NotImplementedError

class BaseCMFMigrator(BaseMigrator):
    """Base migrator for CMF objects
    """

    def migrate_dc(self):
        """Migrates dublin core metadata
        """
        # doesn't work!
        # shure? works for me
        for accessor, mutator in metadataList:
            oldAcc = getattr(self.old, accessor)
            newMut = getattr(self.new, mutator)
            #newAcc = getattr(self.new, accessor)
            newMut(oldAcc())

    def migrate_workflow(self):
        """migrate the workflow state
        """
        wfh = getattr(self.old, 'workflow_history', None)
        if wfh:
            wfh = copyPermMap(wfh)
            self.new.workflow_history = wfh

    def migrate_allowDiscussion(self):
        """migrate allow discussion bit
        """
        if hasattr(self.old, 'allowDiscussion') and \
          hasattr(self.new, 'isDiscussable'):
            self.new.isDiscussable(self.old.allowDiscussion())

    def last_migrate_date(self):
        """migrate creation / last modified date
        
        Must be called as *last* migration
        """
        self.new.setModificationDate(DateTime(self.old.ModificationDate()))
        self.new.creation_date = DateTime(self.old.CreationDate())

class ItemMigrationMixin:
    """Migrates a non folderish object
    """

    def renameOld(self):
        """Renames the old object
        """
        LOG("renameOld | orig_id: " + str(self.orig_id) + "; old_id: " + str(self.old_id))
        LOG(str(self.old.absolute_url()))
        self.parent.manage_renameObject(self.orig_id, self.old_id)

    def createNew(self):
        """Create the new object
        """
        self.parent.invokeFactory(id=self.new_id, type_name=self.toType)
        self.new = getattr(self.parent, self.new_id)
    
    def remove(self):
        """Removes the old item
        """
        if REMOVE_OLD:
            self.parent.manage_delObjects([self.old_id])
    
class FolderMigrationMixin(ItemMigrationMixin):
    """Migrates a folderish object
    """

    def migrate_children(self):
        """Copy childish objects from the old folder to the new one
        
        XXX: Oh hell that's very inefficient and I'm very shure that it will
        blow up the zodb. See alternative
        """
        for obj in self.old.objectValues():
            self.new.manage_clone(obj, obj.getId())
            
    def XXX_migrate_alternativeChildren(self):
        """Just an idea
        
        I don't know wether it works or fails due the ExtensionClass, ZODB and 
        acquisition stuff of zope
        """
        for obj in self.old.objectValues():
            id = obj.getId()
            self.new._setObject(id, aq_base(obj))

class CMFItemMigrator(ItemMigrationMixin, BaseCMFMigrator):
    """
    """
    
class CMFFolderMigrator(FolderMigrationMixin, BaseCMFMigrator):
    """
    """
