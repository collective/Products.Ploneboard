"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
import sys

from AccessControl import getSecurityManager, Permissions

from Compatibility import actionFactory
import Configuration
from Element import MetadataElement, ElementFactory
from Exceptions import NamespaceConflict, ConfigurationError
from Export import MetadataSetExporter
from FormulatorField import listFields
from Index import createIndexes
from Interfaces import IMetadataSet, IOrderedContainer
from Namespace import DefaultNamespace, DefaultPrefix
from ZopeImports import *

from Products.ProxyIndex.ProxyIndex import getIndexTypes

class OrderedContainer(Folder):

    __implements__ = IOrderedContainer

    security = ClassSecurityInfo()

    security.declareProtected(Permissions.copy_or_move, 'moveObject')
    def moveObject(self, id, position):
        obj_idx  = self.getObjectPosition(id)
        if obj_idx == position:
            return None
        elif position < 0:
            position = 0

        metadata = list(self._objects)
        obj_meta = metadata.pop(obj_idx)
        metadata.insert(position, obj_meta)
        self._objects = tuple(metadata)

    security.declareProtected(Permissions.copy_or_move, 'getObjectPosition')
    def getObjectPosition(self, id):

        objs = list(self._objects)
        om = [objs.index(om) for om in objs if om['id']==id ]

        if om: # only 1 in list if any
            return om[0]

        raise NotFound('Object %s was not found' % str(id))

    security.declareProtected(Permissions.copy_or_move, 'moveObjectUp')
    def moveObjectUp(self, id, steps=1, RESPONSE=None):
        """ Move an object up """
        self.moveObject(
            id,
            self.getObjectPosition(id) - int(steps)
            )
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(Permissions.copy_or_move, 'moveObjectDown')
    def moveObjectDown(self, id, steps=1, RESPONSE=None):
        """ move an object down """
        self.moveObject(
            id,
            self.getObjectPosition(id) + int(steps)
            )
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(Permissions.copy_or_move, 'moveObjectTop')
    def moveObjectTop(self, id, RESPONSE=None):
        """ move an object to the top """
        self.moveObject(id, 0)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(Permissions.copy_or_move, 'moveObjectBottom')
    def moveObjectBottom(self, id, RESPONSE=None):
        """ move an object to the bottom """
        self.moveObject(id, sys.maxint)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def manage_renameObject(self, id, new_id, REQUEST=None):
        " "
        objidx = self.getObjectPosition(id)
        method = OrderedContainer.inheritedAttribute('manage_renameObject')
        result = method(self, id, new_id, REQUEST)
        self.moveObject(new_id, objidx)

        return result

InitializeClass(OrderedContainer)

class MetadataSet(OrderedContainer):
    """
    Set of Elements constituting a metadata dialect
    """

    meta_type = 'Metadata Set'
    __implements__ = IMetadataSet

    security = ClassSecurityInfo()

    all_meta_types = (
        {'name':MetadataElement.meta_type,
         'action':'addElementForm'},
        )

    manage_options = (
        {'label':'Elements',
         'action':'manage_main'},
        {'label':'Settings',
         'action':'manage_settings'},
        {'label':'Action',
         'action':'manage_action'},
        )

    security.declareProtected(Configuration.pMetadataManage, 'manage_settings')
    manage_settings = DTMLFile('ui/SetSettingsForm', globals())

    security.declareProtected(Configuration.pMetadataManage, 'manage_action')
    manage_action  = DTMLFile('ui/SetActionForm', globals())

    security.declareProtected(Configuration.pMetadataManage, 'addElementForm')
    addElementForm  = DTMLFile('ui/ElementAddForm', globals())

    manage_main = DTMLFile('ui/SetContainerView', globals())

    initialized = None
    use_action_p = None
    action = None
    title = ''
    description = ''

    def __init__(self, id, title='', description='',
                 metadata_prefix=DefaultPrefix, metadata_uri=DefaultNamespace):

        self.id = id
        self.initialized = None
        self.use_action_p = None
        self.title = ''
        self.description = ''

        # we can't do any verification till after we have a ctx
        self.metadata_uri = metadata_uri
        self.metadata_prefix = metadata_prefix


    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description

    def addMetadataElement(self,
                           id,
                           field_type,
                           index_type,
                           index_p=None,
                           acquire_p=None,
                           read_only_p=None,
                           RESPONSE=None):
        """ """
        element = ElementFactory(id)
        self._setObject(id, element)
        element = self._getOb(id)

        element.editElementPolicy(field_type = field_type,
                                  index_type = index_type,
                                  index_p = index_p,
                                  read_only_p = read_only_p,
                                  acquire_p = acquire_p)

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_main')

    def editAction(self,
                   use_action_p,
                   id,
                   permission,
                   action,
                   condition,
                   category,
                   visible,
                   RESPONSE=None):
        """ CMF Action Provider Support """

        self.use_action_p = not not use_action_p

        self.action = actionFactory(id=id,
                                    title=title,
                                    permission=permission,
                                    category=category,
                                    action=action,
                                    condition=condition,
                                    visible=visible)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def editSettings(self, title, description, ns_uri, ns_prefix, RESPONSE):
        """ Edit Set Settings """

        if self.isInitialized():
            raise ConfigurationError (" Set Already Initialized ")

        self.setNamespace(ns_uri, ns_prefix)
        self.title = title
        self.description = description

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def exportXML(self, RESPONSE=None):
        """ export an xml serialized version of the policy """

        exporter = MetadataSetExporter(self)

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/xml')
            RESPONSE.setHeader('Content-Disposition',
                               'attachment; filename=%s.xml' % self.getId())
        return exporter()

    def setNamespace(self, ns_uri, ns_prefix):
        verifyNamespace(self, ns_uri, ns_prefix)
        self.metadata_prefix = ns_prefix
        self.metadata_uri = ns_uri

    def isInitialized(self):
        return self.initialized

    def setInitialized(self, initialization_flag, RESPONSE=None):
        """ """
        flag = not not initialization_flag

        if flag != self.initialized:
            if self.initialized:
                self.initialized = 0
            else:
                self.initialize()

        if RESPONSE:
            return RESPONSE.redirect('manage_workspace')

    def initialize(self, RESPONSE=None):
        """ initialize the metadata set """
        if self.isInitialized():
            return None

        # install indexes
        indexables = [e for e in self.getElements() if e.index_p]
        catalog = getToolByName(self, 'portal_catalog')
        createIndexes(catalog, indexables)

        self.initialized = 1

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def getNamespace(self):
        return (self.metadata_prefix, self.metadata_uri)

    def getElements(self):
        return self.objectValues(spec='Metadata Element')

    def getElement(self, element_id):
        return self._getOb(element_id)

    def getElementsFor(self, object, mode='view'):

        if mode == 'view':
            guard = 'read_guard'
        else:
            guard = 'write_guard'

        sm = getSecurityManager()

        res = []
        for e in self.getElements():
            if getattr(e, guard).check(sm, e, object):
                res.append(e)
            if mode == 'edit' and e.read_only_p:
                continue
        return res

    def getMetadataSet(self):
        return self

    def getDefaults(self, content):
        res = {}
        for e in self.getElements():
            res[e.getId()] = e.getDefault(content)
        return res

    def listFieldTypes(self):
        return listFields()

    def listIndexTypes(self):
        return getIndexTypes(getToolByName(self, 'portal_catalog'))

    def manage_afterAdd(self, item, container):
        # verify our namespace
        self.setNamespace(self.metadata_uri, self.metadata_prefix)

InitializeClass(MetadataSet)

def verifyNamespace(ctx, uri, prefix):

    sid = ctx.getId()
    container = aq_parent(aq_inner(ctx))

    for s in container.getMetadataSets():
        if s.getId() == sid:
            continue
        if s.metadata_uri == uri:
            raise NamespaceConflict("%s uri is already in use" % uri)
        elif s.metadata_prefix == prefix:
            raise NamespaceConflict("%s prefix is already in use" % prefix)
