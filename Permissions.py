from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Add Entry
PURGE_URL = 'SquidTool: Purge URL'

setDefaultRoles(PURGE_URL, ( 'Manager', 'Member' ) )

