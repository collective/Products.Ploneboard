#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""


"""
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.migration.CPTMigrator import migrateAll
from Products.ATContentTypes.Extensions.toolbox import switchATCT2CMF, switchCMF2ATCT, isSwitchedToATCT

def migrate(self):
    if isSwitchedToATCT(self):
        switched = 1
        switchATCT2CMF(self)
        get_transaction().commit(1)
    else:
        switched = 0
    try:
        return migrateAll(self)
    finally:
        if switched:
            switchCMF2ATCT(self)
