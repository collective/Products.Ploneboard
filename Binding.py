"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import types, copy
from UserDict import UserDict

from Acquisition import Implicit, aq_base, aq_parent
from Products.ZCatalog.ZCatalog import ZCatalog

from zExceptions import Unauthorized
from Exceptions import NotFound, BindingError
from Export import ObjectMetadataExporter
from Index import getIndexNamesFor
import Initialize as BindingInitialize
from Namespace import MetadataNamespace, BindingRunTime
from ZopeImports import Interface, ClassSecurityInfo, InitializeClass
from ZopeImports import PersistentMapping, getToolByName

#################################
### runtime bind data keys
AcquireRuntime = 'acquire_runtime'
ObjectDelegate = 'object_delegate'
MutationTrigger = 'mutation_trigger'

#################################
### Acquired Metadata Prefix Encoding
MetadataAqPrefix = 'metadataAq'
MetadataAqVarPrefix = '_VarName_'

_marker = []


class Data(UserDict):
    """
    We use this as to escape some vagaries with the zope security policy
    when using the __getitem__ interface of the binding
    """
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1


class MetadataBindAdapter(Implicit):

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, content, collection):
        self.content = content

        if isinstance(collection, types.ListType):
            self.ordered_set_names = []
            d = {}
            for s in collection:
                d[s.getId()]=s
                self.ordered_set_names.append(s.getId())
            collection = d
        elif isinstance(collection, types.DictType):
            # no explicit order defined
            self.ordered_set_names = collection.keys()
        else:
            raise BindingError ("metadata sets in wrong format")

        self.collection = collection
        self.cached_values = {}

    #################################
    ### Views
    security.declarePublic('renderXML')
    def renderXML(self, set_id=None, namespace_key=None):
        """
        return an xml serialization of the object's metadata
        """

        if set_id or namespace_key:
            sets = [self._getSet(set_id, namespace_key)]
        else:
            sets = self.collection.values()

        exporter = ObjectMetadataExporter(self, sets)
        return exporter()

    security.declarePublic('renderElementView')
    def renderElementView(self, set_id, element_id):
        element = self.getElement(set_id, element_id)
        data = self._getData(set_id)
        return element.renderView(data.get(element_id, None))

    security.declarePublic('renderElementEdit')
    def renderElementEdit(self, set_id, element_id):
        element = self.getElement(set_id, element_id)
        data = self._getData(set_id, acquire=0)
        return element.renderEdit(data.get(element_id, None))

    #################################
    ### Validation

    security.declarePublic('validate')
    def validate(self, set_id, data, errors=None):
        """
        validate the data. implicit transforms may be preformed.
        """
        return validateData(self, self.collection[set_id], data, errors)

    security.declarePublic('validateFromRequest')
    def validateFromRequest(self, set_id, REQUEST, errors=None):
        """
        validate from request
        """
        data = REQUEST.form.get(set_id)

        if data is None:
            raise NotFound("Metadata for %s/%s not found" % (
                str(set_id),
                str(namespace_key)
                )
                )

        return self.validate(set_id, data.copy(), errors)

    #################################
    ### Storage (invokes validation)

    security.declarePublic('setValues')
    def setValues(self, set_id, data, reindex=0):
        """
        data should be a mutable dictionary

        returns a dictionary of errors if any, or none otherwise
        """
        errors = {}
        data = self.validate(set_id, data, errors)

        if errors:
            return errors

        set = self.collection[set_id]
        self._setData(data, set_id=set_id, reindex=reindex)
        return None

    security.declarePublic('setValuesFromRequest')
    def setValuesFromRequest(self, set_id, REQUEST, reindex=0):
        """
        returns a dictionary of errors if any, or none otherwise
        """
        set = self.collection[set_id]
        data_from_request = REQUEST.form.get(set.getId(), {})

        # We assume that setValuesFromRequest is called for TTW code,
        # i.e. a form submit. This means, we can assume that all fields
        # have been filled and submitted, although this does not necessarily
        # mean, all fields are available in the REQUEST - e.g. for checkboxes
        # turned off... ugh.
        # So, the data dict we provide to setValues needs to contain all
        # elements of the set. This, then, is the main use case (or semantic)
        # difference between setValues and setValuesFromRequest.
        # BTW, we need to take care of subforms too, e.g. in case of datetime
        # fields...
        data = {}
        for e in set.getElements():
            eid = e.getId()
            if hasattr(aq_base(e.field), 'sub_form'):
                for sfid in e.field.sub_form.get_field_ids():
                    sfkey = e.field.generate_subfield_key(sfid, validation=1)
                    data[sfkey] = data_from_request.get(sfkey, '')
            else:
                data[eid] = data_from_request.get(eid, '')
        return self.setValues(set_id, data, reindex)

    #################################
    ### Discovery Introspection // Definition Accessor Interface

    security.declarePublic('getSetNameByURI')
    def getSetNameByURI(self, uri):
        for set in self.collection.values():
            if set.metadata_uri == uri:
                return set.getId()
        raise NotFound(uri)

    security.declarePublic('getSet')
    def getSet(self, set_id):
        """
        to invoke methods on the set requires permissions on
        the set not the content, whereas binding methods
        merely require permissions on the content.
        """
        return self.collection[set_id]

    security.declarePublic('getElement')
    def getElement(self, set_id, element_id):
        return self.getSet(set_id).getElement(element_id)

    security.declarePublic('getSetNames')
    def getSetNames(self):
        """
        return the ids of the metadata sets available for this content
        type.
        """
        return tuple(self.ordered_set_names)

    security.declarePublic('keys')
    keys = getSetNames

    security.declarePublic('getElementNames')
    def getElementNames(self, set_id, mode=None):
        """
        given a set identifier return the ids of the elements
        within the set.
        """
        # XXX
        # if mode is not specified this returns all elements of a set.
        # not all elements visible will be viewable/editable
        set = self.collection[set_id]

        if mode is not None:
            elements = set.getElementsFor(self.content, mode=mode)
        else:
            elements = set.getElements()

        return [e.getId() for e in elements]

    security.declarePublic('isViewable')
    def isViewable(self, set_id, element_id):
        """
        is the element viewable for the content object
        """
        element = self.collection[set_id].getElement(element_id)
        ob = self._getAnnotatableObject()
        return element.isViewable(ob)

    security.declarePublic('isEditable')
    def isEditable(self, set_id, element_id):
        """
        is the element editable for the content object
        """
        element = self.collection[set_id].getElement(element_id)
        ob = self._getAnnotatableObject()
        return element.isEditable(ob)


    security.declarePublic('listAcquired')
    def listAcquired(self):
        """
        compute and return a list of (set_id, element_id)
        values for all metadata which this binding/content
        acquires from above in the containment hiearchy.
        """
        res = []
        ob = self._getAnnotatableObject()

        for s in self.collection.values():
            sid = s.getId()
            data = self._getData(set_id = sid, acquire=0)
            for e in [e for e in s.getElements() if e.isAcquireable()]:
                eid = e.getId()
                if data.has_key(eid) and data[eid]:
                    continue
                name = encodeElement(sid, e.getId())
                try:
                    value = getattr(ob, name)
                except AttributeError:
                    continue
                # filter out any empty metadata fields
                # defined on ourselves to acquire
                if not hasattr(aq_base(ob), name):
                    res.append((sid, eid))

        return res

    #################################
    ### Data Accessor Interface

    security.declarePublic('get')
    def get(self, set_id, element_id=None, acquire=1, no_defaults=0):
        """
        if element_id is specified, only the value of that element is
        returned, otherwise a Data object is returned. Data objects
        implement a mapping interface.

        the acquire flag determines whether or not metadata acquisition
        will be used in retrieving values, acquired values will override
        default values but not values stored on the object.

        the no_defaults flag specifies whether an element's default values
        should be used. default values are only used when there is no
        value stored on the object.

        the use case for no_defaults is whe using tales defaults to defer
        an element's value to another element within the same set. also when
        no_defaults is used not all elements of the set will nesc. be
        in the data object returned only those which were findable.
        """
        data = self._getData(set_id=set_id,
                             acquire=acquire,
                             no_defaults=no_defaults)
        if element_id is not None:
            return data.get(element_id)
        return data

    def __getitem__(self, key):
        if self.collection.has_key(key):
            return self._getData(key)
        raise KeyError(str(key))

    #################################
    ### RunTime Binding Methods

    security.declarePublic('setObjectDelegator')
    def setObjectDelegator(self, method_name):
        """
        we get and set all metadata on a delegated object,
        method should be a callable method on the object
        (acquiring the method is ok) that should take zero
        args, and return an object. if it doesn't return
        an object, we return the default metadata values
        associated (not a good idea).
        """
        assert getattr(self.content, method_name), \
                       "invalid object delegate %s" % method_name

        bind_data = self._getBindData()
        bind_data[ObjectDelegate]=method_name

    security.declarePrivate('getObjectDelegator')
    def getObjectDelegator(self):
        return self._getBindData().get(ObjectDelegate)

    security.declarePublic('clearObjectDelegator')
    def clearObjectDelegator(self):
        bind_data = self._getBindData()
        try:
            del bind_data[ObjectDelegate]
        except KeyError:
            pass
        # invalidate cache
        self.cached_values = {}

        return None

    security.declarePublic('setMutationTrigger')
    def setMutationTrigger(self, set_id, element_id, method_name):
        """
        support for simple events, based on acquired method
        invocation. major use case.. cache invalidation on
        metadata setting.
        """
        assert getattr(self._getAnnotatableObject(), method_name), \
                       "invalid mutation trigger %s" % method_name

        bind_data = self._getBindData()
        tr = bind_data.setdefault(MutationTrigger, {}).setdefault(set_id, {})
        tr[element_id]=method_name

    security.declarePublic('clearMutationTrigger')
    def clearMutationTrigger(self, set_id, element_id=None):
        """
        clear mutation triggers for a particular set or element.

        if element_id is not specified, clear triggers for
        the entire set.
        """

        bind_data = self._getBindData()
        triggers = bind_data[MutationTrigger]

        if element_id is None:
            try:
                del triggers[set_id]
            except KeyError:
                pass
        else:
            try:
                del triggers[set_id][element_id]
            except KeyError:
                pass
        return None

    #################################
    ### Private

    def _getSet(self, set_id=None, namespace_key=None):
        if set_id:
            return self.collection[set_id]
        elif namespace_key:
            return self._getSetByKey(namespace_key)
        else:
            raise NotFound("metadata set not found %s %s"
                           % (set_id, namespace_key))

    def _getBindData(self):
        annotations = getToolByName(self.content, 'portal_annotations')
        metadata = annotations.getAnnotations(self.content, MetadataNamespace)
        bind_data = metadata.get(BindingRunTime)

        if bind_data is None:
            init_handler = BindingInitialize.getHandler(self.content)
            bind_data = metadata.setdefault(BindingRunTime, PersistentMapping())
            if init_handler is not None:
                init_handler(self.content, bind_data)

        return bind_data

    def _getMutationTriggers(self, set_id):
        bind_data = self._getBindData()
        return bind_data.get(MutationTrigger, {}).get(set_id, [])

    def _getAnnotatableObject(self):
        # check for object delegation
        bind_data = self._getBindData()
        object_delegate = bind_data.get(ObjectDelegate)

        # we want to use the content in its original acquisiton
        # context, but because we retrieve it as an attribute
        # it gets wrapped.. content.__of__(binding).__of__(content)
        # so we remove the outer two wrappers to regain the original
        # context
        content = aq_parent(aq_parent(self.content))

        if object_delegate is not None:
            od = getattr(self.content, object_delegate)
            ob = od()
        else:
            ob = content

        return ob

    def _getData(self, set_id=None, namespace_key=None,
                 acquire=1, no_defaults=0):
        """
        find the metadata for the given content object,
        performs runtime binding work as well.

        """

        set = self._getSet(set_id, namespace_key)

        # cache lookup
        data = self.cached_values.get((acquire, set.getId()))
        if data is not None:
            return data

        using_defaults = []
        ob = self._getAnnotatableObject()

        # get the annotation data
        annotations = getToolByName(ob, 'portal_annotations')
        metadata = annotations.getAnnotations(ob, MetadataNamespace)

        saved_data = metadata.get(set.metadata_uri)
        data = Data()

        sid = set.getId()
        element_ids = self.getElementNames(sid)

        if saved_data is None and no_defaults:
            pass
        elif saved_data is None:
            # use the sets defaults
            data.update(set.getDefaults(content=ob))

            # record which elements we used default values for
            using_defaults = element_ids
        else:
            # make a copy so we can modify with acq metadata
            data.update(saved_data)

            if not no_defaults:
                # update individual elements with default values
                # if they don't have a saved value.
                for eid in element_ids:
                    if data.has_key(eid):
                        continue
                    data[eid] = set.getElement(eid).getDefault(content=ob)
                    using_defaults.append(eid)

        # cache metadata
        self.cached_values[ (acquire, set_id) ]=data

        if not acquire:
            return data

        # get the acquired metadata
        hk = data.has_key
        for e in [e for e in set.getElements() if e.isAcquireable()]:
            eid = e.getId()
            if hk(eid) and data[eid] and not eid in using_defaults:
                continue
            aqelname = encodeElement(sid, eid)
            try:
                val = getattr(ob, aqelname)
            except AttributeError:
                continue
            data[eid]=val

        return data

    def _setData(self, data, set_id=None, namespace_key=None, reindex=0):

        set = self._getSet(set_id, namespace_key)
        set_id = set.getId()

        # check for delegates
        ob = self._getAnnotatableObject()

        # filter based on write guard and whether field is readonly
        all_elements = set.getElements()
        all_eids = [e.getId() for e in all_elements]
        elements = [e for e in set.getElementsFor(ob, mode='edit')]
        eids = [e.getId() for e in elements]

        keys = data.keys()

        for k in keys:
            if k in eids:
                continue
            elif k in all_eids:
                raise Unauthorized('Not Allowed to Edit %s in this context' % k)
            else:
                del data[k]

        # fire mutation triggers
        triggers = self._getMutationTriggers(set_id)

        if triggers:
            for k in keys:
                if triggers.has_key(k):
                    try:
                        getattr(ob, triggers[k])()
                    except: # gulp
                        pass

        # update acquireable metadata
        update_list = [e.getId() for e in set.getElements() \
                                 if  e.isAcquireable() and e.getId() in keys]
        sid = set.getId()

        for eid in update_list:
            aqelname = encodeElement(sid, eid)
            value = data[eid]
            if value:
                setattr(ob, aqelname, value)
            else:
                # Try and get rid of encoded attribute on the
                # annotatable object; this will get acquisition
                # of the value working again.
                try:
                    delattr(ob, aqelname)
                except (KeyError, AttributeError), err:
                    pass

        # save in annotations
        annotations = getToolByName(ob, 'portal_annotations')
        metadata = annotations.getAnnotations(ob, MetadataNamespace)

        if metadata.has_key(set.metadata_uri):
            metadata[set.metadata_uri].update(data)
        else:
            metadata[set.metadata_uri] = PersistentMapping(data)

        # invalidate the cache version of the set if any
        # we do a check for cached acquired/non-acquired
        if self.cached_values.has_key((0, set_id)):
            del self.cached_values[(0, set_id)]
        if self.cached_values.has_key((1, set_id)):
            del self.cached_values[(1, set_id)]

        # mark both the content and the annotatable object as changed so
        # on txn commit bindings in other objectspaces get invalidated as well
        ob._p_changed = 1
        self.content._p_changed = 1

        # reindex object
        if reindex:
            reindex_elements = [
                e for e in elements
                if (e.getId() in keys) and e.index_p]
            idx_names = getIndexNamesFor(reindex_elements)
            catalog = getToolByName(ob, 'portal_catalog')
            # cmf compatibility hack
            ZCatalog.catalog_object(catalog, ob, idxs=idx_names)

    def _getSetByKey(self, namespace_key):
        for s in self.collection.values():
            if s.metadata_uri == namespace_key:
                return s
        raise NotFound(str(namespace_key))

InitializeClass(MetadataBindAdapter)

def validateData(binding, set, data, errors_dict=None):
    # XXX completely formulator specific
    from Products.Formulator.Errors import ValidationError

    # Filter out elements not in the data dict, provided the element is
    # not required or the binding already has a value for this element.
    for e in set.getElements():
        eid = e.getId()
        has_a_value = not not binding.get(set.getId(), eid, acquire=0)
        is_required = e.isRequired()

        if hasattr(aq_base(e.field), 'sub_form'):
            # XXX this is really a datetime hack..
            # Fields with subforms will/might have only their marshalled
            # subform ids stored in the data dict. There really isn't a
            # good way to discover which fields are sub form providers,
            # so we just try to introspect.
            # Get one of the subform field ids, just try one.. unfortunately
            # the presence of a subform has little todo with the fields
            # request encoding. sigh.
            sfid = e.field.sub_form.get_field_ids()[0]
            sfkey = e.field.generate_subfield_key(sfid, validation=1)

            if not data.has_key(sfkey) and (not is_required or has_a_value):
                continue

        elif not data.has_key(eid) and (not is_required or has_a_value):
            continue

        try:
            data[eid] = e.validate(data)
        except ValidationError, exception:
            if errors_dict is not None:
                errors_dict[eid] = exception.error_text
            else:
                raise
    return data

def encodeElement(set_id, element_id):
    """
    after experimenting with various mechanisms for doing
    containment based metadata acquisition, using extension class
    acquisition was found to be the quickest way to do the containment
    lookup. as attributes are stored as opaque objects, the current
    implementation decorates the object heirarchy with encoded variables
    corresponding to the metadata specified as acquired. the encoding
    is used to minimize namespace pollution. acquired metadata is only
    specified in this manner on the source object.
    """
    return MetadataAqPrefix + set_id + MetadataAqVarPrefix + element_id

def decodeVariable(name):
    """ decode an encoded variable name... not used """
    assert name.startswith(MetadataAqPrefix)

    set_id = name[len(MetadataAqPrefix):name.find(MetadataAqVarPrefix)]
    e_id = name[name.find(MetadataAqVarPrefix)+len(MetadataAqVarPrefix):]

    return set_id, e_id

