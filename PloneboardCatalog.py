from Products.CMFCore.CatalogTool import CatalogTool

PLONEBOARD_CATALOG_ID = 'ploneboard_catalog'

class PloneboardCatalog(CatalogTool):
    id = PLONEBOARD_CATALOG_ID
    portal_type = meta_type = 'Ploneboard Catalog'

    def enumerateIndexes(self):
        """ """
        standard = CatalogTool.enumerateIndexes(self)
        return standard
               
    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        return standard
