# Copyright (C) 2003-2004 strukturAG <simon@struktur.de>
# http://www.strukturag.com, http://www.icoya.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Patches.

$Id: Patches.py,v 1.9 2004/01/25 21:44:47 kayeva Exp $
"""

__version__ = "$Revision: 1.9 $"

from types import StringType
####################
# <start patches>

# PATCH 1
#
# Makes REQUEST available from the Globals module.
#
# It's needed because context is not available in the __of__ method,
# so we can't get REQUEST with acquisition. And we need REQUEST for
# local properties (see LocalPropertyManager.pu).
#
# This patch was taken from Localizer (http://www.localizer.org)
# so this software runs indepently of Localizer
#
# The patch is inspired in a similar patch by Tim McLaughlin, see
# "http://dev.zope.org/Wikis/DevSite/Proposals/GlobalGetRequest".
# Thanks Tim!!
#

from thread import get_ident
from Acquisition import aq_parent
from ZPublisher import Publish, mapply
from zLOG import LOG, PROBLEM

def get_request():
    """Get a request object"""
    return Publish._requests.get(get_ident(), None)

def new_publish(request, module_name, after_list, debug=0):
    id = get_ident()
    Publish._requests[id] = request
    x = Publish.old_publish(request, module_name, after_list, debug)
    try:
        del Publish._requests[id]
    except KeyError:
        # Some people has reported that sometimes a KeyError exception is
        # raised in the previous line, I haven't been able to reproduce it.
        # This try/except clause seems to work. I'd prefer to understand
        # what is happening.
        LOG('I18NLayer', PROBLEM,
            "The thread number %s don't has a request object associated." % id)

    return x


import Globals
patch = 0
if not hasattr(Globals, 'get_request'):
    # Apply patch
    Publish._requests = {}
    Publish.old_publish = Publish.publish
    Publish.publish = new_publish

    Globals.get_request = get_request
    # First import (its not a refresh operation).
    # We need to apply the patches.
    patch = 1


# PATCH 2
#
# Filters I18NLayer objects which dont represent an object
# patch support to folder base classes to return spec matches 
# for i18nlayer based on containment
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
try:
    from BTrees.OIBTree import OIBTree, union
    from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
except: BTreeFolder2Base=None

def new__filteredItems(self, ids, filt):
    """
    call _old_filteredItems() and strip empty I18NLayers
    """
    result = self._old_filteredItems(ids, filt)
    outtypes=('I18NLayer',)

    i=0
    x=0
    length=len(result)

    while(i < length):
        inc=1
        r = result[x]
        if getattr(r[1], 'portal_type') in outtypes:
            try: typ=r[1].Type()
            except: typ=None
            if typ in outtypes:
                if not _checkPermission(ModifyPortalContent, r[1]):
                    # only show empty I18NLayers when user may modify them
                    del result[x]
                    inc=0
        if inc: x=x+1
        i=i+1

    return result


def new_objectIds(self, spec=None):
    # Returns a list of subobject ids of the current object.
    # If 'spec' is specified, returns objects whose meta_type
    # matches 'spec'.

    # Returns a list of subobject ids of the current object.
    # If 'spec' is specified, returns objects whose meta_type
    # matches 'spec'.

    # we also match i18nlayer subobjects here which match spec
    
    if spec is not None:
        if type(spec)==type('s'):
            spec=[spec]
        set=[]
        for ob in self._objects:
            if ob['meta_type'] in spec:
                set.append(ob['id'])
            elif ob['meta_type'] == 'I18NLayer':
                o=getattr(self, ob['id'])
                if o.ContainmentMetaType() in spec:
                    set.append(ob['id'])
        return set
    # return all if no spec
    return map(lambda i: i['id'], self._objects)


def new_BTreeobjectIds(self, spec=None):
    # Returns a list of subobject ids of the current object.
    # If 'spec' is specified, returns objects whose meta_type
    # matches 'spec'.

    # we also match i18nlayer subobjects here which match spec

    if spec is not None:
        if isinstance(spec, StringType):
            spec = [spec]
        mti = self._mt_index
        set = None
        for meta_type in spec:
            ids = mti.get(meta_type, None)
            if ids is not None:
                set = union(set, ids)
        lids = mti.get('I18NLayer', None)
        if lids is not None:
            ids = OIBTree()
            for id in lids.keys():
                o = self._getOb(id)
                if o.ContainmentMetaType() in spec:
                    ids[id]=lids[id]
                set = union(set, ids)
            
        if set is None:
            return ()
        else:
            return set.keys()
    else:
        return self._tree.keys()


patch2 = 0
if not hasattr(PortalFolder, '_old_filteredItems'):
    # Apply patch
    PortalFolder._old_filteredItems = PortalFolder._filteredItems
    PortalFolder._filteredItems = new__filteredItems
    PortalFolder.objectIds = new_objectIds
    if BTreeFolder2Base: BTreeFolder2Base.objectIds = new_BTreeobjectIds

    # First import (not a refresh)
    # applied patch
    patch2 = 1


# PATCH 3
#
# adds the attribute i18nContent_language = neutral to PortalContent class
# and to PortalFolder class

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolder
patch3 = 0
if not hasattr(PortalContent, 'i18nContent_language'):
    # Apply patch
    PortalContent.i18nContent_language='neutral'
    PortalFolder.i18nContent_language='neutral'

    # First import (not a refresh)
    # applied patch
    patch3 = 1


# PATCH 4
#
# patch title_or_id to not return the translated document id
# patch in PortalContent and PortalFolder

def new_title_or_id(self):
    """
    Utility that returns the title if it is not blank 
    and the id of the layer if inside one otherwise.
    """
    title=self.title
    if callable(title):
        title=title()
    if title: return title
    try:
        parent=aq_parent(self)
        if getattr(parent, 'meta_type', None) == 'I18NLayer':
            return parent.getId()
    except: pass
    return self.getId()    

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolder
patch4 = 0
PortalContent.title_or_id = new_title_or_id
PortalFolder.title_or_id = new_title_or_id

        
# </finished patches>
#####################

