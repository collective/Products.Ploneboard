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

$Id: CalendarSupport.py,v 1.1 2004/05/06 02:28:24 tiran Exp $
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

DATE  = "%Y%m%dT%H%M%S"
DATEZ = "%Y%m%dT%H%M%SZ"

PRODID = "-//AT Content Types//AT Event//EN"

ICS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:%(dtstamp)
CREATED:%(created)
UID:ATEvent-%(uid)
SEQUENCE:0
LAST-MODIFIED:%(modified)
SUMMARY:%(summary)
DTSTART:%(startdate)
DTEND:%(enddate)
"""

ICS_FOOTER = """\
CLASS:PUBLIC
PRIORITY:3
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR
"""

VCS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)
VERSION:1.0

BEGIN:VEVENT
"""

VCS_FOOTER = """\
PRIORITY:3
TRANSP:0
END:VEVENT
END:VCALENDAR
"""

class CalendarSupportMixin:
    """Mixin class for iCal/vCal support
    """
    
    #__implements__ = IHistoryAware

    security       = ClassSecurityInfo()

    actions = ({
        'id'          : 'ics',
        'name'        : 'iCalendar',
        'action'      : 'string:${object_url}/ics',
        'permissions' : (CMFCorePermissions.View, )
         },
         {
        'id'          : 'vcs',
        'name'        : 'vCalendar',
        'action'      : 'string:${object_url}/vcs',
        'permissions' : (CMFCorePermissions.View, )
         },
    )
    
    security.declareProtected(CMFCorePermissions.View, 'getDocumentComparisons')
    def ics(self, REQUEST, RESPONSE):
        """iCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/calendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.ics"' % self.getId())
        out = StringIO()
        out.write(ICS_HEADER % ({ 'prodid'    : PRODID,
                                  'dtstamp'   : DateTime().strftime(DATEZ),
                                  'created'   : DateTime(self.CreationDate()).strftime(DATEZ),
                                  'uid'       : self.UID(),
                                  'modified'  : DateTime(self.ModificationDate()).strftime(DATEZ),
                                  'summary'   : self.Title(),
                                  'startdate' : DateTime(self.start()).strftime(DATEZ),
                                  'enddate'   : DateTime(self.end()).strftime(DATEZ),
                               })
                 )
        # XXX todo
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)
        #DESCRIPTION:
        #LOCATION:
        #CATEGORIES:
        out.write(ICS_FOOTER)
        return out.getvalue()

    def vcs(self, REQUEST, RESPONSE):
        """vCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/x-vCalendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.vcs"' % self.getId())
        out = StringIO()
        out.write(VCS_HEADER % ({ 'prodid'    : PRODID,
                               })
                 )
        # XXX todo
        out.write(VCS_FOOTER)
        return out.getvalue()

InitializeClass(CalendarSupportMixin)
