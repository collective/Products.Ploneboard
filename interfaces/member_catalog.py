
""" 
Member Catalog Interface: taken from portal_catalog
$Id:
"""

from Interface import Attribute
from Products.CMFCore.interfaces.portal_catalog import portal_catalog as IPortalCatalog
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class member_catalog(IPortalCatalog):
    '''This tool interacts with a customized ZCatalog.
    '''
    id = Attribute('id', 'Must be set to "member_catalog"')

