## Script (Python) "indexedOwner"
##title=indexes owner for all content
##parameters=
from ZODB.POSException import ConflictError
try:
    owner_info = context.owner_info()
    owner = '/' + owner_info['path'] + '/' + owner_info['id']
except ConflictError:
    raise
except:
    owner = None

return owner

