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

$Id: ATEvent.py,v 1.11 2004/05/15 00:52:20 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from types import StringType

try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import registerType

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.interfaces.IATEvent import IATEvent
from Products.ATContentTypes.types.schemata import ATEventSchema
from Products.ATContentTypes.CalendarSupport import CalendarSupportMixin


class ATEvent(ATCTContent, CalendarSupportMixin):
    """An Archetype derived version of CMFCalendar's Event"""

    schema         =  ATEventSchema

    content_icon   = 'event_icon.gif'
    meta_type      = 'ATEvent'
    archetype_name = 'AT Event'
    immediate_view = 'event_view'
    default_view   = 'event_view'
    suppl_views    = ()
    newTypeFor     = ('Event', 'CMF Event')
    typeDescription= 'Fill in the details of the event you want to add.'
    typeDescMsgId  = 'description_edit_event'
    assocMimetypes = ()
    assocFileExt   = ('event', )

    __implements__ = ATCTContent.__implements__, IATEvent

    security       = ClassSecurityInfo()
    
    actions = updateActions(ATCTContent, CalendarSupportMixin.actions)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method
        
        Changing the event type changes also the subject. 
        """
        f = self.getField('eventType')
        f.set(self, value, **kw)
        if not alreadySet:
            self.setSubject(value, alreadySet=True, **kw)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setSubject')
    def setSubject(self, value, alreadySet=False, **kw):
        """CMF compatibility method
        
        Changing the subject changes also the event type.
        """
        f = self.getField('subject')
        f.set(self, value, **kw)

        # set the event type to the first subject
        if type(value) is StringType:
            v = (value, )
        elif value:
            v = value[0]
        else:
            v = ()

        if not alreadySet:
            self.setEventType(v, alreadySet=True, **kw)

    security.declareProtected(CMFCorePermissions.View, 'getEventTypes')
    def getEventTypes(self):
        """fetch a list of the available event types from the vocabulary
        """
        metatool = getToolByName(self, "portal_metadata")
        events = metatool.listAllowedSubjects(content_type = "Event")
        return events

registerType(ATEvent, PROJECTNAME)
