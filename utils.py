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

$Id: utils.py,v 1.2 2004/09/17 14:19:33 tiran Exp $
"""

import datetime
from DateTime import DateTime

def dt2DT(date):
    """convert Zope's DateTime to python's datetime
    """
    return DateTime(*date.timetuple()[:6])

def DT2dt(date):
    """convert python's datetime to Zope's DateTime
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    return datetime.datetime(*args)

def toTime(date):
    """get time part of a date
    """
    if isinstance(date, datetime.datetime):
        date = dt2DT(date)
    return date.Time()

def toSeconds(td):
    """Converts a timedelta to an integer representing the number of minutes
    """
    return td.seconds + td.days * 86400
