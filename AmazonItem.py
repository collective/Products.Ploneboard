import amazon
import time

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from config import PROJECT_NAME, ADD_CONTENT_PERMISSION
from Widget import ReadOnlyFloatWidget, ReadOnlyIntegerWidget, ReadOnlyLinesWidget, ReadOnlyStringWidget
from utils import toAscii

"""
      Asin - Amazon ID ("ASIN" number) of this item
      Authors - list of authors
      Availability - "available", etc.
      BrowseList - list of related categories
      Catalog - catalog type ("Book", etc)
      CollectiblePrice - ?, format "$34.95"
      ImageUrlLarge - URL of large image of this item
      ImageUrlMedium - URL of medium image of this item
      ImageUrlSmall - URL of small image of this item
      Isbn - ISBN number
      ListPrice - list price, format "$34.95"
      Lists - list of ListMania lists that include this item
      Manufacturer - manufacturer
      Media - media ("Paperback", "Audio CD", etc)
      NumMedia - number of different media types in which this item is available
      OurPrice - Amazon price, format "$24.47"
      ProductName - name of this item
      ReleaseDate - release date, format "09 April, 1999"
      Reviews - reviews (AvgCustomerRating, plus list of CustomerReview with Rating, Summary, Content)
      SalesRank - sales rank (integer)
      SimilarProducts - list of Product, which is ASIN number
      ThirdPartyNewPrice - ?, format "$34.95"
      URL - URL of this item
"""

content_schema = Schema((
    StringField('id',
                required=0, ## Still actually required, but
                            ## the widget will supply the missing value
                            ## on non-submits
                accessor='getId',
                mutator='setId',
                default=None,
                widget=IdWidget(label='Short Name',
                                label_msgid='label_short_name',
                                description='Short Name is part of the item\'s web address. '
                                            'Should not contain spaces, upper case, underscores '
                                            'or other special characters.',
                                description_msgid='help_shortname',
                                visible={'view' : 'invisible'},
                                i18n_domain="plone"),
               ),

    StringField('asin',
                accessor='getAsin',
                index = (':schema'),
                required=1,
                default='',
                widget=StringWidget(label='ASIN',
                                    description='Amazon ID (ASIN number) of this item',
                                    size=12,),
               ),

    StringField('title',
                accessor='Title',
                searchable=1,
                index = ('TextIndexNG|TextIndex:schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Book Title',
                                            description=None,),
               ),

    TextField('main_page_description',
              default='',
              searchable=1,
              accessor='Description',
              mutator='setDescription',
              storage=MetadataStorage(),
              widget = TextAreaWidget(description = 'Enter your notes for this item', 
                                      description_msgid = 'help_description',
                                      label = 'Notes',
                                      label_msgid = "label_description",
                                      rows = 6,
                                      cols = 60,
                                      i18n_domain = "plone"),
             ),

    LinesField('authors',
               accessor='getAuthors',
               index = (':schema'),
               default='',
               widget=ReadOnlyLinesWidget(label='Authors',
                                          description='List of authors',),
              ),

    FloatField('avg_customer_rating',
                accessor='getAvgCustomerRating',
                index = (':schema'),
                default='',
                widget=ReadOnlyFloatWidget(label='Average Customer Review',
                                           description=None,),
               ),

    StringField('availability',
                accessor='getAvailability',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Availability',
                                            description='"available", etc.',),
               ),

    LinesField('browse_list',
               accessor='getBrowseList',
#               index = (':schema'),
               default='',
               widget=ReadOnlyLinesWidget(label='Browse List',
                                          description='A list of related categories',),
              ),

    StringField('catalog_type',
                accessor='getCatalogType',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Catalog Type',
                                            description='"Book", etc',),
               ),

    StringField('collectible_price',
                accessor='getCollectiblePrice',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Collectible Price',
                                            description='"Book", etc',),
               ),

    StringField('image_url_small',
                accessor='getImageUrlSmall',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Small Image URL',
                                            description='URL of small image of this item',),
               ),

    StringField('image_url_medium',
                accessor='getImageUrlMedium',
                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Medium Image URL',
                                            description='URL of medium image of this item',),
               ),

    StringField('image_url_large',
                accessor='getImageUrlLarge',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Large Image URL',
                                            description='URL of large image of this item',),
               ),

    StringField('isbn',
                accessor='getIsbn',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='ISBN',
                                            description=None,),
               ),

    LinesField('lists',
               accessor='getLists',
#               index = (':schema'),
               default='',
               widget=ReadOnlyLinesWidget(label='Lists',
                                          description='List of ListMania lists that include this item',),
               ),

    StringField('list_price',
                accessor='getListPrice',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='List Price',
                                            description='List price, format "$34.95"',),
               ),

    StringField('manufacturer',
                accessor='getManufacturer',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Manufacturer',
                                            description=None,),
               ),

    StringField('media',
                accessor='getMedia',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Media',
                                            description='"Paperback", "Audio CD", etc',),
               ),

    IntegerField('num_media',
                 accessor='getNumMedia',
#                index = (':schema'),
                 default=1,
                 widget=ReadOnlyStringWidget(label='Number of Media',
                                            description='Number of different media types in which this item is available',),
               ),

    StringField('release_date',
                accessor='getReleaseDate',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Release Date',
                                            description='Release date, format "09 April, 1999"',),
               ),

    LinesField('similar_products',
               accessor='getSimilarProducts',
#               index = (':schema'),
               default='',
               widget=ReadOnlyLinesWidget(label='Similar Products',
                                          description='List of ASIN numbers',),
              ),

    StringField('third_party_new_price',
                accessor='getThirdPartyNewPrice',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Third Party New Price',
                                            description=None,),
               ),

    IntegerField('total_customer_reviews',
                 accessor='getTotalCustomerReviews',
                 default=0,
                 widget=ReadOnlyIntegerWidget(label='Total Customer Reviews',
                                              description=None,),
               ),

    IntegerField('sales_rank',
                 accessor='getSalesRank',
                 index = (':schema'),
                 default=999999999,
                 widget=ReadOnlyIntegerWidget(label='Sales Rank',
                                              description=None,),
               ),

    StringField('amazon_price',
                accessor='getAmazonPrice',
#                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Amazon Price',
                                            description='Amazon price, format "$24.47"',),
               ),

    StringField('amazon_url',
                accessor='getAmazonUrl',
                index = (':schema'),
                default='',
                widget=ReadOnlyStringWidget(label='Amazon URL',
                                            description=None,),
               ),

    ))


# # generate the addAmazonItem method ourselves so we can do some extra initialization
# security = ModuleSecurityInfo('Products.ATAmazon.AmazonItem')
# security.declareProtected(ADD_CONTENT_PERMISSION, 'addAmazonItem')
# def addAmazonItem(self, id, **kwargs):
#     o = AmazonItem(id)
#     self._setObject(id, o)
#     o = getattr(self, id)
#     o.initializeArchetype(**kwargs)


class AmazonItem(BaseContent):
    """ """
    security = ClassSecurityInfo()
    portal_type = meta_type = 'Amazon Item'
    schema = content_schema + ExtensibleMetadata.schema

    # initial values for all values in catalog metadata
    asin = None
    authors = None
    image_url_medium = None
    sales_rank = 999999999
    amazon_url = None
    avg_customer_rating = None
    last_updated = None

    actions = ({ 'id': 'view',
                 'name': 'View',
                 'action': 'string:${object_url}/amazon_item_view',
                 'permissions': (CMFCorePermissions.View,),
                 'category': 'object',
               },
               { 'id': 'amazon_search',
                 'name': 'Amazon Search',
                 'action': 'string:${object_url}/search_amazon',
                 'permissions': (CMFCorePermissions.View,),
                 'category': 'object',
               },
               { 'id': 'details',
                 'name': 'Details',
                 'action': 'string:${object_url}/base_view',
                 'permissions': (CMFCorePermissions.View,),
                 'category': 'object',
               },
              )
              
    immediate_view = 'search_amazon'

    def getAmazonDeveloperKey(self):
        amazon_developer_key = getattr(getToolByName(self, 'portal_properties').site_properties, 'amazon_developer_key', None)
        if amazon_developer_key is None:
            raise ValueError, 'Set your Amazon web services developer key in portal_properties/site_properties/amazon_developer_key'
        return amazon_developer_key.strip()
    def getAmazonAssociateId(self):
        amazon_associate_id = getattr(getToolByName(self, 'portal_properties').site_properties, 'amazon_associate_id', None)
        if amazon_associate_id is None:
            raise ValueError, 'Set your Amazon associate ID in portal_properties/site_properties/amazon_associate_id'
        return amazon_associate_id.strip()
    
    def _init_from_xml(self, item):
        """Initialize an AmazonItem from the xml returned by a search"""
        # Note - I am converting from unicode to ascii all over to keep the
        # catalog from choking.  Ideally stuff should be converted to UTF-8,
        # but (1) I don't know how to do this, and (2) I doubt the catalog
        # is unicode-aware.
        self.last_updated = time.time()
        self.setAsin(toAscii(getattr(item, 'Asin', '')))
        self.setTitle(toAscii(getattr(item, 'ProductName', '')))
        self.setAvailability(toAscii(getattr(item, 'Availability', '')))
        self.setCatalog_type(toAscii(getattr(item, 'Catalog', '')))
        self.setCollectible_price(toAscii(getattr(item, 'CollectiblePrice', '')))
        self.setImage_url_small(toAscii(getattr(item, 'ImageUrlSmall', '')))
        self.setImage_url_medium(toAscii(getattr(item, 'ImageUrlMedium', '')))
        self.setImage_url_large(toAscii(getattr(item, 'ImageUrlLarge', '')))
        self.setIsbn(toAscii(getattr(item, 'Isbn', '')))
        self.setList_price(toAscii(getattr(item, 'ListPrice', '')))
        self.setMedia(toAscii(getattr(item, 'Media', '')))
        self.setManufacturer(toAscii(getattr(item, 'Manufacturer', '')))
        self.setRelease_date(toAscii(getattr(item, 'ReleaseDate', '')))
        sales_rank = getattr(item, 'SalesRank', 999999999)
        self.setSales_rank(getattr(item, 'SalesRank', 999999999))
        self.setThird_party_new_price(toAscii(getattr(item, 'ThirdPartyNewPrice', '')))
        self.setAmazon_price(toAscii(getattr(item, 'OurPrice', '')))
        self.setAmazon_url(toAscii(getattr(item, 'URL', '')))
        
        authors = getattr(item, 'Authors', [])
        if authors != []:
            authors = getattr(authors, 'Author', [])
            if type(authors) != type([]):
                authors = [authors]
        self.setAuthors([toAscii(a) for a in authors])

        browse_list = getattr(item, 'BrowseList', [])
        if browse_list != []:
            browse_list = getattr(browse_list, 'BrowseNode', [])
            if type(browse_list) != type([]):
                browse_list = [browse_list]
            browse_list = [b.BrowseName for b in browse_list if getattr(b, 'BrowseName', '')]
        self.setBrowse_list([toAscii(b) for b in browse_list])

        lists = getattr(item, 'Lists', [])
        if lists != []:
            lists = getattr(lists, 'ListId', [])
            if type(lists) != type([]):
                lists = [lists]
        self.setLists([toAscii(l) for l in lists])

        self.reviews = []
        reviews = getattr(item, 'Reviews', None)
        if reviews is None:
            avg_customer_rating = None
            total_customer_reviews = 0
        else:
            avg_customer_rating = getattr(reviews, 'AvgCustomerRating', None)
            try:
                avg_customer_rating = float(avg_customer_rating)
            except (ValueError, TypeError):
                avg_customer_rating = None
            total_customer_reviews = getattr(reviews, 'TotalCustomerReviews', 0)
            try:
                total_customer_reviews = int(total_customer_reviews)
            except (ValueError, TypeError):
                total_customer_reviews = 0
            customer_reviews = getattr(reviews, 'CustomerReview', [])
            review_list = []
            if type(customer_reviews) != type([]):
                customer_reviews = [customer_reviews]
            for cr in customer_reviews:
                review_list.append(AmazonReview(cr))
            self.reviews = review_list
        self.setAvg_customer_rating(avg_customer_rating)
        self.setTotal_customer_reviews(total_customer_reviews)

        sp = getattr(item, 'SimilarProducts', [])
        if sp != []:
            sp = getattr(sp, 'Product', [])
            if type(sp) != type([]):
                sp = [sp]
        self.setSimilar_products(sp)
            
        self.reindexObject()
        
    def update(self):
        amazon_developer_key = self.getAmazonDeveloperKey()

        if not self.asin:
            return
        matches = None
        try:
            matches = amazon.searchByASIN(self.getAsin(), license_key=amazon_developer_key)
        except IOError:
            pass
        if not matches:
            return
        # assert(len(matches) == 1)
        item = matches[0]
        asin = self.getAsin()
        self._init_from_xml(item)
        assert(self.getAsin() == asin)

    def updateIfOld(self, delta=3600):
        if not self.last_updated or time.time() - self.last_updated > delta:
            self.update()

    def Title(self):
        self.updateIfOld(24*3600)
        return self.title

    def getAsin(self):
        return toAscii(self.asin).strip()

    def getAuthors(self):
        self.updateIfOld(24*3600)
        return self.authors

    def getAvailability(self):
        self.updateIfOld(3600)
        return self.availability

    def getAvgCustomerRating(self):
        self.updateIfOld(24*3600)
        if not type(self.avg_customer_rating) == type(0.0):
            return 0.0
        return self.avg_customer_rating

    def getBrowseList(self):
        self.updateIfOld(24*3600)
        return self.browse_list

    def getCatalogType(self):
        self.updateIfOld(24*3600)
        return self.catalog_type

    def getImageUrlSmall(self):
        self.updateIfOld(24*3600)
        return self.image_url_small
    
    def getImageUrlMedium(self):
        self.updateIfOld(24*3600)
        return self.image_url_medium
    
    def getImageUrlLarge(self):
        self.updateIfOld(24*3600)
        return self.image_url_large
    
    def getIsbn(self):
        self.updateIfOld(24*3600)
        return self.isbn
    
    def getListPrice(self):
        self.updateIfOld(3600)
        return self.list_price
    
    def getMedia(self):
        self.updateIfOld(24*3600)
        return self.media
    
    def getManufacturer(self):
        self.updateIfOld(24*3600)
        return self.manufacturer
    
    def getReleaseDate(self):
        self.updateIfOld(24*3600)
        return self.release_date
    
    def getReviews(self):
        self.updateIfOld(24*3600)
        return self.reviews
    
    def getSalesRank(self):
        self.updateIfOld(24*3600)
        return self.sales_rank

    def getSimilarProducts(self):
        self.updateIfOld(24*3600)
        return self.similar_products

    def getTotalCustomerReviews(self):
        self.updateIfOld(3600)
        return self.total_customer_reviews

    def getThirdPartyNewPrice(self):
        self.updateIfOld(3600)
        return self.third_party_new_price

    def getAmazonPrice(self):
        self.updateIfOld(3600)
        return self.amazon_price

    def getAmazonUrl(self):
        self.updateIfOld(24*3600)
        return self.amazon_url
    
    def powerSearch(self, author='', title='', subject='', isbn='', publisher='', search_type='heavy'):
        s = ''
        if author:
            s += 'author: ' + author.strip()
        if title:
            s += 'title: ' + title.strip()
        if subject:
            s += 'subject: ' + subject.strip()
        if isbn:
            s += 'isbn: ' + isbn.strip()
        if publisher:
            s += 'publisher: ' + publisher.strip()
        matches = amazon.searchByPower(s, type=search_type, license_key=self.getAmazonDeveloperKey())
        items = []
        n = 0
        for m in matches:
            item = AmazonItem(str(n)).__of__(self.getParentNode())
            item.initializeArchetype()
            item._init_from_xml(m)
            items.append(item)
            n += 1
        return items
    
    def priceToFloat(self, p):
        p2 = ''
        for c in p:
            if (c >= '0' and c <= '9') or c == '.':
                p2 += c
        try:
            return float(p2)
        except (ValueError, TypeError):
            return 0.0
    
    
class AmazonReview:
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, customer_review):
        self.summary = toAscii(getattr(customer_review, 'Summary', ''))
        self.comment = toAscii(getattr(customer_review, 'Comment', ''))
        rating = getattr(customer_review, 'Rating', None)
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            rating = None
        self.rating = rating

    def getSummary(self):
        return self.summary
    
    def getComment(self):
        return self.comment
    
    def getRating(self):
        # rating should be an integer or None
        return self.rating

registerType(AmazonItem, PROJECT_NAME)