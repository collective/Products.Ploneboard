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

$Id: ATEvent.py,v 1.3 2004/03/20 16:08:53 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATEvent import IATEvent
from schemata import ATEventSchema


class ATEvent(BaseContent):
    """An Archetype derived version of CMFCalendar's Event"""

    schema         =  ATEventSchema

    content_icon   = 'event_icon.gif'
    meta_type      = 'ATEvent'
    archetype_name = 'AT Event'
    newTypeFor     = 'Event'
    TypeDescription= ''
    assocMimetypes = ()
    assocFileExt   = ('event', )

    __implements__ = BaseContent.__implements__, IATEvent

    security       = ClassSecurityInfo()

    actions = ({
       'id'          : 'view',
       'name'        : 'View',
       'action'      : 'string:${object_url}/event_view',
       'permissions' : (CMFCorePermissions.View,)
        },
       {
       'id'          : 'edit',
       'name'        : 'Edit',
       'action'      : 'string:${object_url}/atct_edit',
       'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        },
       )

    # XXX event type is alias for Subject!

    # XXX contact_* are string and not methods in the original API

    # fetch a list of the available event types
    # from the vocabulary
    security.declareProtected(CMFCorePermissions.View, 'getEventTypes')
    def getEventTypes(self):
        metadata = getToolByName(self, "portal_metadata")
        events = metadata.listAllowedSubjects(content_type = "Event")
        return events

registerType(ATEvent, PROJECTNAME)
