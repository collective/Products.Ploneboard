## Script (Python) "indexedUsersWithLocalRoles"
##title=
##parameters= 
from ZODB.POSException import ConflictError

try:
   usersWithLocalRoles = \
                       dict(context.get_local_roles()).keys()
except ConflictError:
    raise
except :
    usersWithLocalRoles = []

return usersWithLocalRoles
