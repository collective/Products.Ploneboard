"""
Common Zope Imports

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_inner, aq_parent
from ComputedAttribute import ComputedAttribute
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Globals import DTMLFile, InitializeClass
from Interface import Base as Interface
from ZODB.PersistentMapping import PersistentMapping

from Compatibility import getToolByName, UniqueObject

# py2.2.2 forward decl
try:
    True, False
except:
    True = 1
    False = 0

