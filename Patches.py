# Copyright (C) 2003 strukturAG <simon@struktur.de>
#                    http://www.strukturag.com, http://www.icoya.com

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

$Id: Patches.py,v 1.1 2003/03/25 16:46:55 longsleep Exp $
"""

__version__ = "$Revision: 1.1 $"

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
from ZPublisher import Publish, mapply

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
        # XXX
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

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent

def new__filteredItems(self, ids, filt):
    """
    call _old_filteredItems() and strip empty I18NLayers
    """
    result = self._old_filteredItems(ids, filt)
    outtypes=('I18NLayer',)
    i=0
    for r in result:
        if getattr(r[1], 'portal_type') in outtypes:
	    try: typ=r[1].Type()
            except: typ=None
	    if typ in outtypes:
                if not _checkPermission(ModifyPortalContent, r[1]):
                    # only show empty I18NLayers when user may modify them
                    del result[i]
        i=i+1
                
    return result

patch2 = 0
if not hasattr(PortalFolder, '_old_filteredItems'):
    # Apply patch
    PortalFolder._old_filteredItems = PortalFolder._filteredItems
    PortalFolder._filteredItems = new__filteredItems

    # First import (not a refresh)
    # applied patch
    patch2 = 1

# PATCH 3
#
# adds the attribute i18nContent_language = neutral to PoralContent class
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

# </finished patches>
#####################
