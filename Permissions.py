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

$Id: Permissions.py,v 1.3 2004/07/13 13:12:55 dreamcatcher Exp $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Topic and Event related permissions into one place
AddTopics = 'Add portal topics'
ChangeTopics = 'Change portal topics'
ChangeEvents = 'Change portal events'

# Set up default roles for permissions
setDefaultRoles(AddTopics, ('Manager',))
setDefaultRoles(ChangeTopics, ('Manager', 'Owner',))
setDefaultRoles(ChangeEvents, ('Manager', 'Owner',))

# Add a AT Content Type
ADD_CONTENT_PERMISSION = CMFCorePermissions.AddPortalContent

# Add a AT Topic / criterion
ADD_TOPIC_PERMISSION   = AddTopics
