"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: util.py,v 1.1 2004/09/16 17:42:05 ajung Exp $
"""

import urllib

def redirect(RESPONSE, dest, msg=None,**kw):
    """ redirect() helper method """
    
    if RESPONSE is not None:    
        url = dest + "?"
        if msg:
            url += "portal_status_message=%s&" % urllib.quote(msg)
        if kw:
            url += '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in kw.items()])
        RESPONSE.redirect(url) 
