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
"""History awareness

$Id: CalendarSupport.py,v 1.3 2004/05/06 12:14:28 tiran Exp $
""" 
__author__  = 'Christian Heimes, Christian Theune'
__docformat__ = 'restructuredtext'

from cStringIO import StringIO
import quopri # quoted printable

from DateTime import DateTime
from Globals import InitializeClass


from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
#from Products.ATContentTypes.interfaces.IHistoryAware import IHistoryAware

DATE = "%Y%m%dT%H%M%SZ"

PRODID = "-//AT Content Types//AT Event//EN"

# iCal header and footer
ICS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)s
VERSION:2.0

"""

ICS_FOOTER = """\

END:VCALENDAR
"""

# iCal event
ICS_EVENT_START = """\
BEGIN:VEVENT
DTSTAMP:%(dtstamp)s
CREATED:%(created)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
DTSTART:%(startdate)s
DTEND:%(enddate)s
"""

ICS_EVENT_END = """\
CLASS:PUBLIC
PRIORITY:3
TRANSP:OPAQUE
END:VEVENT

"""

# vCal header and footer
VCS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)s
VERSION:1.0
"""

VCS_FOOTER = """\

END:VCALENDAR
"""

# vCal event
VCS_EVENT_START = """\
BEGIN:VEVENT
DTSTART:%(startdate)s
DTEND:%(enddate)s
DCREATED:%(created)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
"""

VCS_EVENT_END = """\
PRIORITY:3
TRANSP:0
END:VEVENT

"""

class CalendarSupportMixin:
    """Mixin class for iCal/vCal support
    """
    
    #__implements__ = IHistoryAware

    security       = ClassSecurityInfo()

    actions = ({
        'id'          : 'ics',
        'name'        : 'iCalendar',
        'action'      : 'string:${object_url}/ics_view',
        'permissions' : (CMFCorePermissions.View, )
         },
         {
        'id'          : 'vcs',
        'name'        : 'vCalendar',
        'action'      : 'string:${object_url}/vcs_view',
        'permissions' : (CMFCorePermissions.View, )
         },
    )

    security.declareProtected(CMFCorePermissions.View, 'getICal')
    def getICal(self):
        """get iCal data
        """
        out = StringIO()
        map = { 
            'dtstamp'   : DateTime().strftime(DATE),
            'created'   : DateTime(self.CreationDate()).strftime(DATE),
            'uid'       : self.UID(),
            'modified'  : DateTime(self.ModificationDate()).strftime(DATE),
            'summary'   : self.Title(),
            'startdate' : self.start().strftime(DATE),
            'enddate'   : self.end().strftime(DATE),
            }
        out.write(ICS_EVENT_START % map)
        description = self.Description()
        if description:
            out.write('DESCRIPTION:%s\n' % description)
        location = self.getLocation()
        if location:
            out.write('LOCATION:%s\n' % location)
        eventType = self.getEventType()
        if eventType:
            out.write('CATEGORIES:%s\n' % eventType)
        # XXX todo
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)
        out.write(ICS_EVENT_END)
        return out.getvalue()

    
    security.declareProtected(CMFCorePermissions.View, 'ics_view')
    def ics_view(self, REQUEST, RESPONSE):
        """iCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/calendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.ics"' % self.getId())
        out = StringIO()
        out.write(ICS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getICal())
        out.write(ICS_FOOTER)
        return n2rn(out.getvalue())

    security.declareProtected(CMFCorePermissions.View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        out = StringIO()
        map = { 
            'dtstamp'   : DateTime().strftime(DATE),
            'created'   : DateTime(self.CreationDate()).strftime(DATE),
            'uid'       : self.UID(),
            'modified'  : DateTime(self.ModificationDate()).strftime(DATE),
            'summary'   : self.Title(),
            'startdate' : self.start().strftime(DATE),
            'enddate'   : self.end().strftime(DATE),
            }
        out.write(VCS_EVENT_START % map)
        description = self.Description()
        if description:
            out.write('DESCRIPTION:%s\n' % description)
        location = self.getLocation()
        if location:
            out.write('LOCATION:%s\n' % location)
        out.write(VCS_EVENT_END)
        # XXX todo

    security.declareProtected(CMFCorePermissions.View, 'vcs_view')
    def vcs_view(self, REQUEST, RESPONSE):
        """vCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/x-vCalendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.vcs"' % self.getId())
        out = StringIO()
        out.write(VCS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getVCal())
        out.write(VCS_FOOTER)
        return n2rn(out.getvalue())

InitializeClass(CalendarSupportMixin)


def n2rn(s):
    return s.replace('\n', '\r\n')

