"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: util.py,v 1.6 2004/09/29 14:57:19 spamsch Exp $
"""

import urllib
import types
import inspect
from md5 import md5
from ExtensionClass import ExtensionClass

def redirect(RESPONSE, dest, msg=None,**kw):
    """ redirect() helper method """
    
    if RESPONSE is not None:    
        url = dest + "?"
        if msg:
            url += "portal_status_message=%s&" % urllib.quote(msg)
        if kw:
            url += '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in kw.items()])
        RESPONSE.redirect(url) 

def create_signature(schema):
    """ Replacement for buggy signature impl in AT Schema """

    s = 'Schema: {'
    for f in schema.fields():

        s += '%s:%s.%s-%s.%s: {' % \
             (f.__name__, inspect.getmodule(f.__class__).__name__, f.__class__.__name__,
              inspect.getmodule(f.widget.__class__).__name__, f.widget.__class__.__name__)

        s += _property_extraction(f._properties)
        s += _property_extraction(f.widget.__dict__)
        s += '}'

    s = s + '}'
    return md5(s).digest()

def _property_extraction(properties):

    s = ''
    disallowed = [types.ClassType, types.MethodType, types.ModuleType, type(ExtensionClass)]

    sorted_keys = properties.keys()
    sorted_keys.sort()
            
    for k in sorted_keys:
        if (type(k) not in disallowed):
            if (type(properties[k]) not in disallowed):
                s = s + '%s:%s,' % (k, properties[k])

    return s
