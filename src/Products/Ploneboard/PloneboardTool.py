from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from OFS.Image import File
from OFS.Folder import Folder
from ZPublisher.HTTPRequest import FileUpload
from ZODB.PersistentMapping import PersistentMapping

from zope.interface import implements

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.Ploneboard.config import PLONEBOARD_TOOL
from Products.Ploneboard.interfaces import IPloneboardTool

class PloneboardTool(UniqueObject, Folder, ActionProviderBase):
    implements(IPloneboardTool)

    id = PLONEBOARD_TOOL
    meta_type = 'Ploneboard Tool'

    security = ClassSecurityInfo()
    def __init__(self):
        self.transforms = PersistentMapping()

    security.declarePrivate('registerTransform')
    def registerTransform(self, name, module, friendlyName=None):
        tr_tool = getToolByName(self, 'portal_transforms')
        if name not in tr_tool.objectIds():
            tr_tool.manage_addTransform(name, module)
            wasAdded = True
        else:
            wasAdded = False

        if not friendlyName:
            friendlyName = name

        if name not in self.transforms:
            self.transforms[name] = {'enabled' : True,
                                     'friendlyName' : friendlyName,
                                     'wasAdded' : wasAdded
                                     }

    security.declarePrivate('unregisterTransform')
    def unregisterTransform(self, name):
        tr_tool = getToolByName(self, 'portal_transforms')
        if self.transforms[name]['wasAdded']:
            try:
                tr_tool._delObject(name)
            except AttributeError, e:
                pass
        del self.transforms[name]

    security.declareProtected(ManagePortal, 'enableTransform')
    def enableTransform(self, name, enabled=True):
        """Change the activity status for a transform."""
        self.transforms[name]['enabled'] = enabled

    security.declarePrivate('unregisterAllTransforms')
    def unregisterAllTransforms(self):
        tr_tool = getToolByName(self, 'portal_transforms')
        for transform_name in self.getTransforms():
            if not self.transforms[transform_name] or \
                    self.transforms[transform_name].get('wasAdded', False):
                try:
                    tr_tool._delObject(transform_name)
                except AttributeError:
                    pass
        self.transforms.clear()

    security.declareProtected(ManagePortal, 'getTransforms')
    def getTransforms(self):
        """Returns list of transform names."""
        return self.transforms.keys()

    security.declareProtected(ManagePortal, 'getTransformFriendlyName')
    def getTransformFriendlyName(self, name):
        """Returns a friendly name for the given transform."""
        return self.transforms[name]['friendlyName']

    security.declareProtected(View, 'getEnabledTransforms')
    def getEnabledTransforms(self):
        """Returns list of names for enabled transforms"""
        return [name for name in self.transforms.keys() if self.transforms[name]['enabled']]

    security.declareProtected(View, 'performCommentTransform')
    def performCommentTransform(self, orig, **kwargs):
        """This performs the comment transform - also used for preview."""
        transform_tool = getToolByName(self, 'portal_transforms')

        content_type=kwargs.get("content_type", "text/plain")

        # This one is very important, because transform object has no
        # acquisition context inside it, so we need to pass it our one
        context=kwargs.get('context', self)


        data = transform_tool._wrap(content_type)

        for transform in self.getEnabledTransforms():
            data = transform_tool.convert(transform, orig, data, context)
            orig = data.getData()

        return orig

    # File upload - should be in a View once we get formcontroller support in Views
    security.declareProtected(View, 'getUploadedFiles')
    def getUploadedFiles(self):
        request = self.REQUEST

        result = []
        files = request.get('files', [])

        if not files:
            return []

        sdm = getToolByName(self, 'session_data_manager', None)

        if sdm is not None:
            pt = getToolByName(self, 'plone_utils')
            hassession = sdm.hasSessionData()

            for file in files:
                if isinstance(file, basestring) and hassession:
                    # Look it up from session
                    oldfile = request.SESSION.get(file, None)
                    if oldfile is not None:
                        result.append(oldfile)
                if isinstance(file, FileUpload):
                    if file:
                        filename = file.filename.split('\\')[-1]
                        id = pt.normalizeString(filename)
                        ct = file.headers.getheader('content-type')
                        if ct is None:
                            ct = ''
                        newfile = File(id, id, file, ct)
                        request.SESSION[id] = newfile
                        result.append(newfile)

            # delete files form session if not referenced
            new_filelist = [x.getId() for x in result]
            old_filelist = hassession and request.SESSION.get('ploneboard_uploads', []) or []
            for removed in [f for f in old_filelist if f not in new_filelist]:
                del request.SESSION[f]
            if hassession or new_filelist:
                request.SESSION['ploneboard_uploads'] = new_filelist

        return result

    security.declareProtected(View, 'clearUploadedFiles')
    def clearUploadedFiles(self):
        # Get previously uploaded files with a reference in request
        # + files uploaded in this request
        # XXX Add variable to keep track of filenames?
        request = self.REQUEST

        sdm = getToolByName(self, 'session_data_manager', None)

        if sdm is not None:
            if sdm.hasSessionData():
                old_filelist = request.SESSION.get('ploneboard_uploads', None)
                if old_filelist is not None:
                    for file in old_filelist:
                        if request.SESSION.has_key(file):
                            del request.SESSION[file]
                    del request.SESSION['ploneboard_uploads']


InitializeClass(PloneboardTool)
registerToolInterface(PLONEBOARD_TOOL, IPloneboardTool)
