from common import *
import sys, traceback, StringIO
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

class MigrationError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return 'MigrationError: %s' % self.msg

class Walker:
    """Walks through the system and migrates every object it finds
    """
    
    def __init__(self, migrator, portal=None):
        self.migrator = migrator
        self.fromType = self.migrator.fromType
        self.toType = self.migrator.toType
        self.subtransaction = self.migrator.subtransaction
        self.out = []
        self.portal = portal
        
    def go(self):
        """runner
        
        Call it to start the migration
        :return: migration notes
        :rtype: list of strings
        """
        self.enableGlobalAddable()
        try:
            self.migrate(self.walk())
        finally:
            self.resetGlobalAddable()
        return self.getOutput()
    
    __call__ = go

    def walk(self):
        """Walks around and returns all objects which needs migration
        
        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        raise NotImplementedError
    
    def enableGlobalAddable(self):
        """Set implicitly addable to true
        
        XXX This is a required hack :/
        """
        ttool = getToolByName(self.portal, 'portal_types')
        ftiTo = ttool.getTypeInfo(self.toType)
        ftiFrom = ttool.getTypeInfo(self.fromType)
        self.toGlobalAllow = ftiTo.globalAllow() 
        self.fromGlobalAllow = ftiFrom.globalAllow()
        ftiTo.global_allow = 1
        ftiFrom.global_allow = 1

    def resetGlobalAddable(self):
        """
        """
        ttool = getToolByName(self.portal, 'portal_types')
        ftiTo = ttool.getTypeInfo(self.toType)
        ftiFrom = ttool.getTypeInfo(self.fromType)
        ftiTo.global_allow = self.toGlobalAllow
        ftiFrom.global_allow = self.fromGlobalAllow

    def migrate(self, objs):
        """Migrates the objects in the ist objs
        """
      
        for obj in objs:
            msg=('Migrating %s from %s to %s ... ' % 
                            ('/'.join(obj.getPhysicalPath()),
                             self.fromType, self.toType, ))
            LOG(msg)
            self.out.append(msg)
            
            migrator = self.migrator(obj)
            try:
                # run the migration
                migrator.migrate()
            except Exception, err: # except all!
                # aborting transaction
                get_transaction().abort()

                # printing exception
                exc = sys.exc_info()
                out=StringIO.StringIO()
                traceback.print_tb(exc[2], limit=None, file=out)
                tb = '%s\n%s\n' % (err, out.getvalue())

                msg = 'ERROR: \n%s' % tb
                LOG(msg)
                self.out[-1]+=msg

                # stop migration process after an error
                # the transaction was already aborted by the migrator itself
                raise MigrationError(tb)
            else:
                LOG('done')
                self.out[-1]+='done'
            if self.subtransaction and \
              (len(self.out) % self.subtransaction) == 0:
                # submit a subtransaction after every X (default 30)
                # migrated objects to safe your butt
                get_transaction().commit(1)
                LOG('comitted...')
                
    def getOutput(self):
        """Get migration notes
        
        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        return '\n'.join(self.out)
    
class CatalogWalker(Walker):
    """Walker using portal_catalog
    """
    
    def __init__(self, migrator, catalog, portal=None):
        Walker.__init__(self, migrator)
        self.catalog = catalog
        self.portal = aq_parent(catalog)
        
    def walk(self):
        """Walks around and returns all objects which needs migration
        
        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        ret = []
        LOG("fromType: " + str(self.fromType))
        brains = self.catalog(portal_type = self.fromType)
        for brain in brains:
            obj = brain.getObject()
            if obj:
                ret.append(obj)
        return ret

class RecursiveWalker(Walker):
    """Walk recursivly through a directory stucture
    """

    def __init__(self, migrator, base, checkMethod, portal=None):
        Walker.__init__(self, migrator)
        self.base=base
        self.checkMethod = checkMethod
        self.list = []
        self.portal = base

    def walk(self):
        """
        """
        self.recurse(self.base)
        return self.list

    def recurse(self, folder):
        for obj in folder.objectValues():
            if self.checkMethod(obj):
                self.list.append(obj)
            if obj.isPrincipiaFolderish:
                self.recurse(obj)
