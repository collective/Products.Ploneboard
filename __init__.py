"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Products.PythonScripts.Utility import allow_module
from Globals import ImageFile, package_home  

import Configuration
import Compatibility
import Collection
import Set
import Element
import Binding
import MetadataTool

# save our fs path for install methods
ProductHome = package_home(globals())

# Allow Errors to be imported TTW
allow_module('Products.CMFMetadata.Exceptions')

misc_ = {
    'up'     : ImageFile('www/up.gif', globals()),
    'down'   : ImageFile('www/down.gif', globals()),
    'top'    : ImageFile('www/top.gif', globals()),
    'bottom' : ImageFile('www/bottom.gif', globals()),
    'metadatatool.png': ImageFile('www/metadatatool.png', globals()),
    'metadataset.png': ImageFile('www/metadataset.png', globals()),
    'typemapping.png': ImageFile('www/typemapping.png', globals()),
    'collection.png': ImageFile('www/collection.png', globals()),
    'type.png': ImageFile('www/type.png', globals())
    }
                                                                                
