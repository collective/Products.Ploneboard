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

$Id: Validators.py,v 1.4 2004/03/17 20:46:43 tiran Exp $
""" 
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import re

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
            # no mxTidy installed
            return 1
        instance = kw['instance']
        field    = kw['field']
        mimetype = field.getContentType(instance)
        if MX_TIDY_MIMETYPES and mimetype not in MX_TIDY_MIMETYPES:
            # do not filter this mime type
            # XXX Doesn't work right now
            #print mimetype
            return 1
        else:
            #print 'tidy: '+mimetype
            pass
        result   = mx_tidy(wrapValueInHTML(value), **MX_TIDY_OPTIONS)
        nerrors, nwarnings, outputdata, errordata = result
        #outputdata=unwrappedValueFromHTML(outputdata)
        errors= nerrors+nwarnings
        if errors:
            return ("Validation Failed(%s): \n %s" % (self.name, parseErrorData(errordata)))
        else:
            return 1

validation.register(TidyHtmlValidator('isTidyHtml'))

def wrapValueInHTML(value):
    """Wrap the data in a valid html construct to remove the missing title error
    """
    return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
</head>
<body>
%s
</body>
</html>
""" % value

def unwrappedValueFromHTML(value):
    """Remove the html stuff around the body
    
    Good: This method is easy
    Bad:  This methods is using hard coded values
    """
    lst = value.split('\n')
    lst = lst[7:]   # remove <!DOCTYPE ... <body>
    lst = lst[:-4] # remove </body></html>\n\n
    return ''.join(lst)

def parseErrorData(data):
    """Parse the error data to change some stuff
    """
    lst = data.split('\n')
    # XXX re matching against line 15 column ...
    # substract 11 lines from line
    return ''.join(lst)
