from common import *

class Walker:
    """Walks through the system and migrates every object it finds
    """
    
    def __init__(self, migrator):
        self.migrator = migrator
        self.fromType = self.migrator.fromType
        self.toType = self.migrator.toType
        self.subtransaction = self.migrator.subtransaction
        self.out = []
        
    def go(self):
        """runner
        
        Call it to start the migration
        :return: migration notes
        :rtype: list of strings
        """
        self.migrate(self.walk())
        return self.getOutput()
    
    __call__ = go

    def walk(self):
        """Walks around and returns all objects which needs migration
        
        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        raise NotImplementedError
    
    def migrate(self, objs):
        """Migrates the objects in the ist objs
        """
      
        for obj in objs:
            msg=('Migrating %s from %s to %s ... ' % 
                            ('/'.join(obj.getPhysicalPath()),
                             self.fromType, self.toType, ))
            LOG(msg)
            self.out.append(msg)
            
            (success, msg) = self.migrator(obj)()
            if success:
                LOG('done')
                self.out[-1]+='done\n'
            else:
                msg='ERROR: \n %s\n' % msg
                LOG(msg)
                self.out[-1]+=msg
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
    
    def __init__(self, migrator, catalog):
        Walker.__init__(self, migrator)
        self.catalog = catalog
        
    def walk(self):
        """Walks around and returns all objects which needs migration
        
        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        ret = []
        brains = self.catalog(portal_type = self.fromType)
        LOG("fromType: " + str(self.fromType))
        for brain in brains:
            obj = brain.getObject()
            if obj:
                ret.append(obj)
        return ret

