"""
Access handlers are used to create a metadata binding
adapter for a particular piece of content. handlers
may be registered either for a specific content
type or as a default accessor to be used when no
more specific content type is found.

signature for a handler is::

  def access_handler(tool, content_type, content)

and should return a metadata binding adapter or
raise an exception.

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Binding import MetadataBindAdapter
from Compatibility import getContentType
from Exceptions import BindingError

_default_accessor = None
_typeAccessHandlers = {}

def registerAccessHandler(content_type, handler):
    assert callable(handler)
    global _typeAccessHandlers, _default_accessor

    if content_type is None:
        _default_accessor = handler
    else:
        _typeAccessHandlers[content_type]=handler

def getAccessHandler(content_type):
    handler = _typeAccessHandlers.get(content_type)
    if handler is None:
        return _default_accessor
    return handler

def invokeAccessHandler(tool, content):
    ct = getContentType(content)
    handler = getAccessHandler(ct)
    if handler is None:
        raise BindingError("no access handler found for %s" % ct)
    return handler(tool, ct, content)

def default_accessor(tool, content_type, content):
    type_mapping = tool.getTypeMapping()
    metadata_sets = type_mapping.getMetadataSetsFor(content_type)

    if not metadata_sets:
        raise BindingError("no metadata sets defined for %s" % content_type)

    return MetadataBindAdapter(content, metadata_sets).__of__(content)


registerAccessHandler(None, default_accessor)
