"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: util.py,v 1.5 2004/09/27 17:43:49 ajung Exp $
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

    disallowed = [types.ClassType, types.MethodType, types.ModuleType, type(ExtensionClass)]
    s = 'Schema: {'
    for f in schema.fields():

        s += '%s:%s.%s-%s.%s: {' % \
             (f.__name__, inspect.getmodule(f.__class__).__name__, f.__class__.__name__,
              inspect.getmodule(f.widget.__class__).__name__, f.widget.__class__.__name__)

        sorted_keys = f._properties.keys()
        sorted_keys.sort()
            
        for k in sorted_keys:
            if (type(k) not in disallowed):
                if (type(f._properties[k]) not in disallowed):
                    s = s + '%s:%s,' % (k, f._properties[k])
                    
        s = s + '}'

    s = s + '}'
    return md5(s).digest()
