from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_chain

from Products.CMFPlone.CatalogTool import CatalogTool as BaseTool
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from Products.Ploneboard.config import PLONEBOARD_CATALOG

try:
    from zope.interface import providedBy
except ImportError:
    def providedBy(obj):
        return tuplize(obj.__implements__)


# Use extensible object wrapper to always list the interfaces
def object_implements(object, portal, **kw):
    return [i.getName() for i in providedBy(object).flattened()]

registerIndexableAttribute('object_implements', object_implements)


class Record:
    """ A simple helper class for carrying the 'extra'-payload to
    index constructors.
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


class PloneboardCatalog(BaseTool):
    id = PLONEBOARD_CATALOG
    portal_type = meta_type = 'Ploneboard Catalog'

    security = ClassSecurityInfo()

#    def enumerateIndexes(self):
#        """ """
#        standard = BaseTool.enumerateIndexes(self)
#        return standard

#    def enumerateColumns( self ):
#        """Return field names of data to be cached on query results."""
#        standard = BaseTool.enumerateColumns(self)
#        return standard

    security.declarePublic( 'enumerateIndexes' )
    def enumerateIndexes( self ):
    #   Return a list of ( index_name, type ) pairs for the initial index set.
        return  ( ('UID'            , 'FieldIndex',     None)
                , ('object_implements', 'KeywordIndex', None)
                , ('SearchableText' , 'TextIndex',      None) # To be used for not exact match
                , ('created'        , 'DateIndex',      None)
                , ('modified'       , 'DateIndex',      None)
                , ('allowedRolesAndUsers', 'KeywordIndex', None)
                , ('review_state'   , 'FieldIndex',     None)
                , ('meta_type'      , 'FieldIndex',     None)
                , ('getId'          , 'FieldIndex',     None)
                , ('inReplyTo'      , 'FieldIndex',     None)
                , ('path'           , 'ExtendedPathIndex' , None)
                , ('portal_type'    , 'FieldIndex',     None)
                , ('startendrange'  , 'DateRangeIndex', {'since_field':'start', 'until_field':'end'})
                )

    security.declarePublic( 'enumerateColumns' )
    def enumerateColumns( self ):
        #   Return a sequence of schema names to be cached.
        return ( 'UID'
               , 'Title'
               , 'review_state'
               , 'getIcon'
               , 'created'
               , 'Creator'
               , 'effective'
               , 'expires'
               , 'modified'
               , 'CreationDate'
               , 'EffectiveDate'
               , 'ExpiresDate'
               , 'ModificationDate'
               , 'portal_type'
               , 'getId'
               , 'inReplyTo'
               )


    def _initIndexes(self):
        """Set up indexes and metadata, as enumared by enumerateIndexes() and
        enumerateColumns (). Subclasses can override these to inject additional
        indexes and columns.
        """
        base = aq_base(self)
        addIndex = self.addIndex
        addColumn = self.addColumn

        # Content indexes
        self._catalog.indexes.clear()
        for (index_name, index_type, extra) in self.enumerateIndexes():
            if extra is None:
               addIndex( index_name, index_type)
            else:
                if isinstance(extra, basestring):
                    p = Record(indexed_attrs=extra)
                elif isinstance(extra, dict):
                    p = Record(**extra)
                else:
                    p = Record()
                addIndex( index_name, index_type, extra=p )

        # Cached metadata
        self._catalog.names = ()
        self._catalog.schema.clear()
        for column_name in self.enumerateColumns():
            addColumn( column_name )

