"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: ManagedSchema.py,v 1.1 2004/09/12 07:27:21 ajung Exp $
"""

from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import ManagedSchema

class ManagedSchema(ManagedSchema):
    """ We wrap the ManagedSchema class in case we need something
        special.
    """

    security = ClassSecurityInfo()

InitializeClass(ManagedSchema)

