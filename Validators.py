from Products.validation import validation
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

$Id: Validators.py,v 1.1 2004/03/08 10:48:40 tiran Exp $
""" 
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.validation.interfaces import ivalidator
from Products.validation.validators import RegexValidator 

class EmptyEmailValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        if str(value) == '':
            return 1
        else:
            return validation.validate('isEmail', value)

validation.register(EmptyEmailValidator('isEmptyEmail'))

class EmptyUrlValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        if str(value) == '':
            return 1
        else:
            return validation.validate('isUrl', value)

validation.register(EmptyUrlValidator('isEmptyUrl'))

class EmptyInternationalPhoneNumberValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        if str(value) == '':
            return 1
        else:
            return validation.validate('isInternationalPhoneNumber', value)

validation.register(EmptyInternationalPhoneNumberValidator('isEmptyInternationalPhoneNumber'))
