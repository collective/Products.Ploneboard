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

$Id: Validators.py,v 1.3 2004/03/17 19:38:57 tiran Exp $
""" 
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from config import *
if HAS_MX_TIDY:
    from mx.Tidy import tidy as mx_tidy

if VALIDATION_IN_PRODUCTS:
    from Products.validation import validation
    from Products.validation.interfaces import ivalidator
    from Products.validation.validators import RegexValidator
else:
    from validation import validation
    from validation.interfaces import ivalidator
    from validation.validators import RegexValidator


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

class TidyHtmlValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kw):
        if not HAS_MX_TIDY:
            return 1
        instance = kw['instance']
        field    = kw['field']
        mimetype = field.getContentType(instance)
        nerrors, nwarnings, outputdata, errordata = mx_tidy(value, **MX_TIDY_OPTIONS)
        print nerrors, nwarnings
        print errordata
        return 1
        #return ("Validation Failed(%s): " % self.name)

validation.register(TidyHtmlValidator('isTidyHtml'))
