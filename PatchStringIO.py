# -*- coding: latin1 -*-
# Copyright (C) 2000-2002  Juan David Ibáñez Palomar <j-david@noos.fr>
# (this copyright notice is encoding in ISO-8859-1 (Latin1))

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


# PATCH 1
#
# Makes REQUEST available from the Globals module.
#
# It's needed because context is not available in the __of__ method,
# so we can't get REQUEST with acquisition. And we need REQUEST for
# local properties (see LocalPropertyManager.pu).
#
# This patch is at the beginning to be sure code that requires it
# doesn't breaks.
#
# This pach is inspired in a similar patch by Tim McLaughlin, see
# "http://dev.zope.org/Wikis/DevSite/Proposals/GlobalGetRequest".
# Thanks Tim!!
#

from thread import get_ident
from ZPublisher import Publish, mapply

def get_request():
    """Get a request object"""
    return Publish._requests.get(get_ident(), None)

def new_publish(request, module_name, after_list, debug=0):
    Publish._requests[get_ident()] = request
    x = Publish.old_publish(request, module_name, after_list, debug)
    try:
        del Publish._requests[get_ident()]
    except KeyError:
        # already deleted?
        pass

    return x

if not hasattr(Publish, '_requests'):
    # Apply patch
    Publish._requests = {}
    Publish.old_publish = Publish.publish
    Publish.publish = new_publish

    import Globals
    Globals.get_request = get_request

# Fix uses of StringIO with a Unicode-aware StringIO
from Products.PageTemplates.PageTemplate import PageTemplate
from TAL.TALInterpreter import TALInterpreter
from StringIO import StringIO as originalStringIO
from types import UnicodeType
class unicodeStringIO(originalStringIO):
    def write(self, s):
        if isinstance(s, UnicodeType):
            response = get_request().RESPONSE
            try:
                s = response._encode_unicode(s)
            except AttributeError:
                # not an HTTPResponse
                pass
        originalStringIO.write(self, s)


if hasattr(TALInterpreter, 'StringIO'):
    # Simply patch the StringIO method of TALInterpreter and PageTemplate
    # on a new Zope
    def patchedStringIO(self):
        return unicodeStringIO()
    TALInterpreter.StringIO = patchedStringIO
    PageTemplate.StringIO = patchedStringIO
