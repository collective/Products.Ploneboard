"""
$Id:
"""

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.utils import UniqueObject
from interfaces.member_catalog import member_catalog as IMemberCatalogTool
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFPlone.CatalogTool import CatalogTool as BaseTool
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo

#class MemberCatalogTool(UniqueObject, ZCatalog, ActionProviderBase):
class MemberCatalogTool(BaseTool):
    
    """ Member Catalog is a Catalog Tool based on Plone Catalog Tool for indexing member related data/objects """

    __implements__ = (IMemberCatalogTool, ActionProviderBase.__implements__)

    id = 'member_catalog'
    meta_type = portal_type = 'Member Catalog Tool'
    manage_options = ( ZCatalog.manage_options +
                       ActionProviderBase.manage_options +
                       ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                        ,)
                       )

    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):
        # Makes sure the SearchableText index is a ZCTextIndex
        if item is self and not hasattr(aq_base(self), 'member_lexicon'):
            class args:
                def __init__(self, **kw):
                    self.__dict__.update(kw)

            self.manage_addProduct[ 'ZCTextIndex' ].manage_addLexicon(
                'member_lexicon',
                elements=[
                args(group= 'Case Normalizer' , name= 'Case Normalizer' ),
                args(group= 'Stop Words' , name= " Don't remove stop words" ),
                args(group= 'Word Splitter' , name= "Unicode Whitespace splitter" ),
                ]
                )

            extra = args( doc_attr = 'SearchableText',
                          lexicon_id = 'member_lexicon',
                          index_type  = 'Okapi BM25 Rank' )

            if 'SearchableText' in self.indexes():
                self.manage_delIndex(['SearchableText'])
            self.manage_addIndex('SearchableText', 'ZCTextIndex', extra=extra)

            extra = args( doc_attr = 'getId',
                          lexicon_id = 'member_lexicon',
                          index_type  = 'Okapi BM25 Rank' )


            self.manage_delIndex(['getId'])
            self.manage_addIndex('getId', 'ZCTextIndex', extra=extra)
