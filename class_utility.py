import string
import re
import threading
import string

# Base classes global vars management
_BASECLASSESLOCK = threading.RLock()
_BASECLASSES = {}
_BASEMETALOCK = threading.RLock()
_BASEMETA = {}

def showaq(self, indent=''):
    "showaq"
    rval = ""
    obj = self
    base = getattr(obj, 'aq_base', obj)
    try: id = base.id
    except: id = str(base)
    try: id = id()
    except: pass
                         
    if hasattr(obj, 'aq_self'):
        if hasattr(obj.aq_self, 'aq_self'):
            rval = rval + indent + "(" + id + ")\n"
            rval = rval + indent + "|  \\\n"
            rval = rval + showaq(obj.aq_self, '|   ' + indent)
            rval = rval + indent + "|\n"
        if hasattr(obj, 'aq_parent'):
            rval = rval + indent + id + "\n"
            rval = rval + indent + "|\n"
            rval = rval + showaq(obj.aq_parent, indent)
    else:
        rval = rval + indent + id + "\n"
    return rval


def listBaseMetaTypes(cl, reverse = 0):
    """
    listBaseMetaTypes(cl, reverse = 0) => list of strings

    List all base meta types for this class.
    """
    # Look for the class in _BASEMETA cache
    try:
        return _BASEMETA[cl][reverse]

    except KeyError:
        _populateBaseMetaTypes(cl)
        return listBaseMetaTypes(cl, reverse)

def isBaseMetaType(meta, cl):
    try:
        return _BASEMETA[cl][2].has_key(meta)

    except KeyError:
        _populateBaseMetaTypes(cl)
        return isBaseMetaType(meta, cl)

def _populateBaseMetaTypes(cl):
    """Fill the base classes structure"""
    # Fill the base classes list
    try:
        ret = [cl.meta_type]
    except AttributeError:
        ret = []
        
    for b in cl.__bases__:
        ret = list(listBaseMetaTypes(b, 1)) + ret

    # Fill the base classes dict
    bases = {}
    for b in ret:
        bases[b] = 1

    _BASEMETALOCK.acquire()
    try:
        rev = ret[:]
        rev.reverse()
        _BASEMETA[cl] = (tuple(rev), tuple(ret), bases)
    finally:
        _BASEMETALOCK.release()

def objectIds(container, meta_types = []):
    """
    """
    return map(lambda x: x[0], objectItems(container, meta_types))

def objectValues(container, meta_types = []):
    """
    """
    return map(lambda x: x[1], objectItems(container, meta_types))

def objectItems(container, meta_types = []):
    """
    objectItems(container, meta_types = [])
    Same as a container's objectItem method, meta_types are scanned in the base classes too.
    Ie. all objects derivated from Folder will be returned by objectItem(x, ['Folder'])
    """
    # Convert input type
    if type(meta_types) not in (type(()), type([])):
        meta_types = [meta_types]

    # Special case where meta_types is empty
    if not meta_types:
        return container.objectItems()

    # Otherwise : check parent for each meta_type
    ret = []
    for (id, obj) in container.objectItems():
        for mt in meta_types:
            if isBaseMetaType(mt, obj.__class__):
                ret.append((id, obj))
                break

    return ret
        


def listBaseClasses(cl, reverse = 0):
    """
    listBaseClasses(cl, reverse = 0) => list of classes
    
    List all the base classes of an object.
    When reverse is 0, return the self class first.
    When reverse is 1, return the self class last.

    WARNING : reverse is 0 or 1, it is an integer, NOT A BOOLEAN ! (optim issue)
    
    CACHE RESULTS

    WARNING : for optimization issues, the ORIGINAL tuple is returned : please do not change it !
    """
    # Look for the class in _BASECLASSES cache
    try:
        return _BASECLASSES[cl][reverse]

    except:
        _populateBaseClasses(cl)
        return listBaseClasses(cl, reverse)


def isBaseClass(base, cl):
    """
    isBaseClass(base, cl) => Boolean
    Return true if base is a base class of cl
    """
    try:
        return _BASECLASSES[cl][2].has_key(base)
    except:
        _populateBaseClasses(cl)
        return isBaseClass(base, cl)


def _populateBaseClasses(cl):
    """Fill the base classes structure"""
    # Fill the base classes list
    ret = [cl]
    for b in cl.__bases__:
        ret = list(listBaseClasses(b, 1)) + ret

    # Fill the base classes dict
    bases = {}
    for b in ret:
        bases[b] = 1

    _BASECLASSESLOCK.acquire()
    try:
        rev = ret[:]
        rev.reverse()
        _BASECLASSES[cl] = (tuple(rev), tuple(ret), bases)
    finally:
        _BASECLASSESLOCK.release()

