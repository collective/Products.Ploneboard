from ZODB.PersistentMapping import PersistentMapping

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
import Globals

def importModuleFromName(module_name):
    """ import and return a module by its name """
    __traceback_info__ = (module_name, )
    m = __import__(module_name)
    try:
        for sub in module_name.split('.')[1:]:
            m = getattr(m, sub)
    except AttributeError, e:
        raise ImportError(str(e))
    return m

class TransformDataProvider(Implicit):
    """ Base class for data providers """
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    
    def __init__(self):
        self.config = PersistentMapping()
        self.config_metadata = PersistentMapping()
        
        self.config.update({'inputs' : {} })
        self.config_metadata.update({
            'inputs' : {
                'key_label' : '', 
                'value_label' : '', 
                'description' : ''}
            })

    security.declarePublic('setElement')
    def setElement(self, inputs):
        """ inputs - dictionary, but may be extended to new data types"""
        self.config['inputs'].update(inputs)
            
    def delElement(self, el):
        """ el - dictionary key"""
        del self.config['inputs'][el]
        
    security.declarePublic('getElements')
    def getElements(self):
        """ Returns mapping """
        return self.config['inputs']
    
    security.declarePublic('getConfigMetadata')
    def getConfigMetadata(self):
        """ Returns config metadata """
        return self.config_metadata['inputs']
    
Globals.InitializeClass(TransformDataProvider)
