## Script (Python) "getAmazonItems"
##title=Get initial id for an AmazonItem
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=n=5, item_folder_id='.books'

# This script is fairly expensive to call, so make sure the results are
# cached.  If you display pricing information in the portlet, you should
# cache for no more than 1 hour to comply with Amazon's licensing terms.
# Other fields may be cached for longer periods of time -- see the Amazon
# web services license agreement for details.

def toint(x):
    # convert to an int without raising an exception so we can handle sorting
    # for objects that don't have a sales rank for whatever reason
    try:
        return int(x)
    except (ValueError, TypeError):
        return 999999999
    
def getAmazonItemsFromCatalog(items, asins, n, path):
    # Grab amazon items from the catalog, sort them by sales rank, then add
    # any new items to our list of items.  Instantiate the objects as we add
    # them to our list so their info can get updated from Amazon if need be.
    results = context.portal_catalog.searchResults(portal_type='Amazon Item', path=path, review_state='published', sort_index="getSalesRank")
    #    results.sort(lambda x, y: cmp(toint(x.getSalesRank), toint(y.getSalesRank)))
    for r in results:
        o = r.getObject()
        asin = o.getAsin()
        if not asins.has_key(asin):
            items.append(r.getObject())
            asins[asin] = 1
            if len(items) == n:
                return

items = []
asins = {}
if n == 0:
    return items
# check for a folder with id book_folder_id
ids = container.objectIds()
if item_folder_id in ids:
    folder = getattr(container, item_folder_id)
    for c in folder.contentValues(filter='Amazon Item', sort_on='sales_rank'):
        asin = c.getAsin()
        if not asins.has_key(asin):
            items.append(c)
            asins[asin] = 1
            if len(items) == n:
                return items

# not enough items - look in folders below this one
getAmazonItemsFromCatalog(items, asins, n, path='/'.join(container.getPhysicalPath()))

if len(items) < n:
    # still not enough - look in the whole site
    getAmazonItemsFromCatalog(items, asins, n, path='/'.join(context.portal_url.getPortalObject().getPhysicalPath()))
    
return items