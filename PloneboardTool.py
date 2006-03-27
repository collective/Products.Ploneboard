from AccessControl import ClassSecurityInfo
import Globals
from OFS.Folder import Folder
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import File
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import CMFCorePermissions
#from permissions import AddAttachment
from Products.CMFCore.utils import getToolByName
from ZODB.PersistentMapping import PersistentMapping
from Products.Ploneboard.utils import importModuleFromName
from Acquisition import aq_base
from Products.Ploneboard.config import PLONEBOARD_TOOL


class PloneboardTool(UniqueObject, Folder, ActionProviderBase):
    id = PLONEBOARD_TOOL
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

    # File upload - should be in a View once we get formcontroller support in Views
    security.declareProtected(CMFCorePermissions.View, 'getUploadedFiles')
    def getUploadedFiles(self):

        request = self.REQUEST

        result = []
        files = request.get('files', [])
        
        if not files:
            return []

        sdm = getToolByName(self, 'session_data_manager', None)
        hassession = sdm.hasSessionData()

        for file in files:
            if isinstance(file, basestring) and hassession:
                # Look it up from session
                oldfile = request.SESSION.get(file, None)
                if oldfile is not None:
                    result.append(oldfile)
            if isinstance(file, FileUpload):
                if file:
                    newfile = File(file.filename, file.filename, file)
                    request.SESSION[file.filename] = newfile
                    result.append(newfile)

        # delete files form session if not referenced
        new_filelist = [x.getId() for x in result]
        old_filelist = hassession and request.SESSION.get('ploneboard_uploads', []) or []
        for removed in [f for f in old_filelist if f not in new_filelist]:
            del request.SESSION[f]
        if hassession or new_filelist:
            request.SESSION['ploneboard_uploads'] = new_filelist
            
        return result

    security.declareProtected(CMFCorePermissions.View, 'clearUploadedFiles')
    def clearUploadedFiles(self):
        # Get previously uploaded files with a reference in request
        # + files uploaded in this request
        # XXX ADD VARIABLE THAT KEEPS TRACK OF FILE NAMES
        request = self.REQUEST

        sdm = getToolByName(self, 'session_data_manager', None)
        hassession = sdm.hasSessionData()

        if hassession:
            old_filelist = request.SESSION.get('ploneboard_uploads', [])
            for file in old_filelist:
                if request.SESSION.has_key(file):
                    del request.SESSION[file]
            del request.SESSION['ploneboard_uploads']


Globals.InitializeClass(PloneboardTool)
