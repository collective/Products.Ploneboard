"""
Type Specific Initialization of Metadata Binding Runtime Data
not really meant for public api exposure (certainly not ttw)

Handler Signature is as follows

def metadata_initialization(content, bind_data)

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Compatibility import getContentType

_default_initializer = None

_typeInitHandlers = {}

def registerInitHandler(content_type, handler):
    assert callable(handler)
    global _typeInitHandlers, _default_initializer

    if content_type is None:
        _default_initializer = handler
    else:
        _typeInitHandlers[content_type]=handler

def getHandler(content):
    ct = getContentType(content)

    handler = _typeInitHandlers.get(ct)

    if handler is None and _default_initializer:
        return _default_initializer

    # possibly none
    return handler


