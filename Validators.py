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

$Id: Validators.py,v 1.14 2004/05/09 23:15:18 tiran Exp $
""" 
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import *

from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator
from Products.validation.validators.RegexValidator import RegexValidator

import re
from ZPublisher.HTTPRequest import FileUpload

from TAL.TALParser import TALParser
from TAL.HTMLTALParser import HTMLTALParser
from TAL.TALGenerator import TALGenerator
from Products.PageTemplates.Expressions import getEngine

if HAS_MX_TIDY:
    from mx.Tidy import tidy as mx_tidy

# matches something like 'line 15 column 1 - Warning: missing ...'
RE_MATCH_WARNING = re.compile('^line (\d+) column (\d+) - Warning: (.*)$')
WARNING_LINE = 'line %d column %d - Warning: %s'

# matches something like 'line 15 column 1 - Error: missing ...'
RE_MATCH_ERROR = re.compile('^line (\d+) column (\d+) - Error: (.*)$')
ERROR_LINE = 'line %d column %d - Error: %s'

# the following regex is safe because *? matches the minimal text in the body tag
# and .* matches the maximum text between two body tags including other body tags
# if they exists
RE_BODY = re.compile('<body[^>]*?>(.*)</body>', re.DOTALL )

# subtract 11 line numbers from the warning/error
SUBTRACT_LINES = 11

validatorList = []

class TALValidator:
    """Validates a text to be valid TAL code
    
    """

    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        gen = TALGenerator(getEngine(), xml=1, source_file=None)
        parser = HTMLTALParser(gen)
        try:
            parser.parseString(value)
        except Exception, err:
            return ("Validation Failed(%s): \n %s" % (self.name, err))
        return 1

validatorList.append(TALValidator('isTAL', title='', description=''))


class TidyHtmlValidator:
    """use mxTidy to check HTML
    
    Fail on errors and warnings
    Do not clean up the value
    """

    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        if not (HAS_MX_TIDY and MX_TIDY_ENABLED):
            # no mxTidy installed
            return 1

        request = kw['REQUEST']
        field   = kw['field']

        result = doTidy(value, field, request)
        if result is None:
            return 1

        nerrors, nwarnings, outputdata, errordata = result
        errors = nerrors + nwarnings

        if errors:
            return ("Validation Failed(%s): \n %s" % (self.name, errordata))
        else:
            return 1

validatorList.append(TidyHtmlValidator('isTidyHtml', title='', description=''))


class TidyHtmlWithCleanupValidator:
    """use mxTidy to check HTML
    
    Fail only on errors
    Clean up
    """

    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kw):
        if not (HAS_MX_TIDY and MX_TIDY_ENABLED):
            # no mxTidy installed
            return 1

        request = kw['REQUEST']
        field   = kw['field']

        result = doTidy(value, field, request, cleanup=1)
        if result is None:
            return 1

        nerrors, nwarnings, outputdata, errordata = result
        errors = nerrors

        # save the changed output in the request
        tidyAttribute = '%s_tidier_data' % field.getName()
        request[tidyAttribute] = outputdata

        if nwarnings:        
            tidiedFields = list(request.get('tidiedFields', []))
            tidiedFields.append(field)
            request.set('tidiedFields', tidiedFields)

        if errors:
            return ("Validation Failed(%s): \n %s" % (self.name, errordata))
        else:
            return 1


validatorList.append(TidyHtmlWithCleanupValidator('isTidyHtmlWithCleanup', title='', description=''))


for validator in validatorList:
    # register the validators
    validation.register(validator)


def doTidy(value, field, request, cleanup=0):
    """Tidy the data in 'value' for the field in the current request
    
    Optional cleanup:
      * removes header/footer of the output data 
      * Removes warnings from the error data
    
    Return None for 'nothing done'
    else return (nerrors, nwarnings, outputdata, errordata)
    """
    # we can't use the mimetype from the field because it's updated *after*
    # validation so we must get it from the request
    tf_name     = '%s_text_format' % field.getName()
    text_format = getattr(request, tf_name, '')

    # MX_TIDY_MIMETYPES configuration option isn't empty
    # and the current text_format isn't in the list
    if MX_TIDY_MIMETYPES and text_format not in MX_TIDY_MIMETYPES:
        # do not filter this mime type
        return None

    # it's a file upload
    if isinstance(value, FileUpload):
        # XXX *mmh* ok it's a file upload but a file upload could destroy
        # the layout, too. Maybe we are doomed?
        return 1

    result = mx_tidy(wrapValueInHTML(value), **MX_TIDY_OPTIONS)
    nerrors, nwarnings, outputdata, errordata = result

    # parse and change the error data
    errordata = parseErrorData(errordata, removeWarnings=cleanup)
    if cleanup:
        # unwrap tidied output data
        outputdata = unwrapValueFromHTML(outputdata)

    return nerrors, nwarnings, outputdata, errordata

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

def unwrapValueFromHTML(value):
    """Remove the html stuff around the body
    """
    # get the body text
    result = RE_BODY.search(value)
    if result:
        body = result.group(1)
    else:
        raise ValueError('%s is not a html string' % value)

##    # remove 2 spaces from the beginning of each line
##    nlines = []
##    for line in body.split('\n'):
##        print line
##        if line[:2] == '  ':
##            nlines.append(line[2:])
##        else:
##            nlines.append(line)
##
##    return '\n'.join(nlines)
    return body

def parseErrorData(data, removeWarnings=0):
    """Parse the error data to change some stuff
    """
    lines  = data.split('\n')
    nlines = []
    for line in lines:
        # substract 11 lines from line
        error = RE_MATCH_ERROR.search(line)
        if error:
            # an error line
            lnum, cnum, text = error.groups()
            lnum  = int(lnum) - SUBTRACT_LINES
            cnum  = int(cnum)
            nlines.append(ERROR_LINE % (lnum, cnum, text))
        else:
            warning = RE_MATCH_WARNING.search(line)
            if warning and not removeWarnings:
                # a warning line and add warnings to output
                lnum, cnum, text = warning.groups()
                lnum  = int(lnum) - SUBTRACT_LINES
                cnum  = int(cnum)
                nlines.append(WARNING_LINE % (lnum, cnum, text))
            else:
                # something else
                nlines.append(line)
    return '\n'.join(nlines)
