"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import Configuration
import Compatibility

import Collection
import Set
import Element
import Binding
import MetadataTool

from Globals import ImageFile

# Allow Errors to be imported TTW
from Products.PythonScripts.Utility import allow_module
allow_module('Products.CMFMetadata.Exceptions')

misc_ = {
    'up'     : ImageFile('www/up.gif', globals()),
    'down'   : ImageFile('www/down.gif', globals()),
    'top'    : ImageFile('www/top.gif', globals()),
    'bottom' : ImageFile('www/bottom.gif', globals()),
    }

