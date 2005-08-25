from AccessControl import ClassSecurityInfo
import Globals
from OFS.Folder import Folder
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import CMFCorePermissions
#from permissions import AddAttachment
from Products.CMFCore.utils import getToolByName
from ZODB.PersistentMapping import PersistentMapping
from Products.Ploneboard.utils import importModuleFromName
from Acquisition import aq_base

class PloneboardTool(UniqueObject, Folder, ActionProviderBase):
    id = 'portal_ploneboard'
    meta_type = 'Ploneboard Tool'
    
    security = ClassSecurityInfo()
    def __init__(self):
        # {'name' : {'transform' : '', 'dataprovider' : '', 'transform_status' : '' }}
        self.transforms_config = PersistentMapping()
    
    def registerTransform(self, name, module):
        tr_tool = getToolByName(self, 'portal_transforms')
        tr_tool.manage_addTransform(name, module)
        
        transform = tr_tool._getOb(name)
        
        dprovider = None
        m = importModuleFromName(module)
        if hasattr(m, 'registerDataProvider'):
            dprovider = m.registerDataProvider()
        
        self.transforms_config[name] = {'transform' : aq_base(transform),
                                        'dataprovider' : dprovider,
                                        'transform_status' : 1}

    def unregisterTransform(self, name):
        tr_tool = getToolByName(self, 'portal_transforms')
        tr_tool._delObject(name)
        del self.transforms_config[name]

    def updateTransform(self, name, **kwargs):
        """ Change status of transform.
            Status may be - 'enabled' or 'disabled' 
        """
        transform_status = kwargs.get('transform_status')
        self.transforms_config[name]['transform_status'] = transform_status

    def unregisterAllTransforms(self):
        tr_tool = getToolByName(self, 'portal_transforms')
        for transform_name, transform_object, transform_status in self.getTransforms():
            try:
                tr_tool._delObject(transform_name)
            except AttributeError, e:
                # _delObject couldn't find the transform_name. Must be gone already.
                pass
        self.transforms_config.clear()

    def getTransforms(self):
        """ Returns list of tuples - (transform_name, transform_object, transform_status) """
        return [(transform_name, val['transform'], val['transform_status']) for transform_name, val in self.transforms_config.items()]
    
    def getEnabledTransforms(self):
        """ Returns list of tuples - (transform_name, transform_object) """
        return [(transform_name, val['transform']) for transform_name, val in self.transforms_config.items() if val['transform_status']]

    security.declarePublic('getDataProviders')
    def getDataProviders(self):
        """ Returns list of tuples - (transform_name, dprovider_object) """
        return [(transform_name, val['dataprovider']) for transform_name, val in self.transforms_config.items() if val['dataprovider'] is not None]

    def getDataProvider(self, name):
        return self.transforms_config[name]['dataprovider']

    def hasDataProvider(self, name):
        if self.transforms_config[name]['dataprovider']:
            return 1
        return 0

    security.declareProtected(CMFCorePermissions.View, 'performCommentTransform')
    def performCommentTransform(self, orig, **kwargs):
        """ This performs the comment transform - also used for preview """
        transform_tool = getToolByName(self, 'portal_transforms')
        
        # This one is very important, because transform object has no 
        # acquisition context inside it, so we need to pass it our one
        if kwargs.get('context', None) is None:
            kwargs.update({ 'context' : self })

        data = transform_tool._wrap('text/plain')
        
        for transform in map(lambda x: x[1], self.getEnabledTransforms()):
            data = transform.convert(orig, data, **kwargs)
            orig = data.getData()
            transform_tool._setMetaData(data, transform)
        
        orig = orig.replace('\n', '<br/>')
        return orig


Globals.InitializeClass(PloneboardTool)
