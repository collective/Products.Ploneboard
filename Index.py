"""
functions for installing and removing indexes for
metadata elements in a zcatalog.

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Products.ProxyIndex import ProxyIndex
from Compatibility import index_expression_template, getToolByName
from UserDict import UserDict

def createIndexes(catalog, elements):

    all_indexes = catalog.indexes()

    for e in elements:
        idx_id  = createIndexId(e)
        extra   = createIndexArguements(e)

        if idx_id in all_indexes:
            continue

        catalog.addIndex(idx_id, ProxyIndex.ProxyIndex.meta_type, extra)
        all_indexes.append(idx_id)

    return None

def removeIndexes(catalog, elements):

    all_indexes = catalog.indexes()

    for e in elements:
        idx_id = createIndexId(e)

        if not idx_id in all_indexes:
            continue

        catalog.delIndex(idx_id)
        all_indexes.remove(idx_id)

    return None

def getIndexNamesFor(elements):
    res = []
    for e in elements:
        res.append(createIndexId(e))
    return res

def createIndexId(element):
    ms = element.getMetadataSet()
    return "%s%s" % (ms.metadata_prefix, element.getId())

def createIndexArguements(element):

    d = ProxyIndex.RecordStyle()

    # try to get the element's index construction key/value pair
    if element.index_constructor_args is not None:
        d.update(element.index_constructor_args)

    d['idx_type'] = element.index_type
    d['value_expr'] = createIndexExpression(element)

    # we setup the idx context manually ourselves..
    # proxyindex needs to find the zcatalog in the containement
    # hierarchy to introspect the pluggable indexes.
    d['idx_context'] = getToolByName(element, 'portal_catalog')

    return d

def createIndexExpression(element):
    return index_expression_template % (
        element.getMetadataSet().getId(),
        element.getId()
        )

