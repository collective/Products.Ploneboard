##parameters=field

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: atse_field_default.py,v 1.1 2004/09/12 07:27:25 ajung Exp $
"""

try:
    return field.getDefault()
except:
    return field.getDefault(context)
