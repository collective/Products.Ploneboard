"""
##############################################################################
#
# Copyright (c) 2003 struktur AG and Contributors. # All Rights Reserved.
# # This software is subject to the provisions of the Zope Public License,# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# $Id: catalogawarehook.py,v 1.1 2003/12/10 00:04:06 longsleep Exp $ (Author: $Author: longsleep $)
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware

# NOTE: we hook into the reindexmethods
#       any reindex also invalidates the cache of this object

def reindexObject(self, idxs=[]):
    """
    first run real reindex
    afterwards prune squid cache
    """
    self._real_reindexObject(idxs=idxs)
    try:
        portal_squid = getToolByName(self, 'portal_squid', None)
        if portal_squid: portal_squid.pruneObject(self)
    except: pass

# monkey patch it
CMFCatalogAware._real_reindexObject=CMFCatalogAware.reindexObject
CMFCatalogAware.reindexObject=reindexObject

