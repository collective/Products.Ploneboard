## Script (Python) "getInitialAmazonId"
##title=Get initial id for an AmazonItem
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item

authors = item.getAuthors()
ids = container.objectIds()
base_id = ''
if authors:
    st = authors[0].strip().lower().split()[-1]
    for c in st:
        if c >= 'a' and c < 'z':
            base_id += c
    if base_id and not base_id in ids:
        return base_id
    
if not base_id:
    base_id = 'asin' + item.getAsin()
    if not base_id in ids:
        return base_id
    base_id += '_'

id = base_id

n = 1
while id in ids:
    id = base_id + str(n)
    n += 1
return id