from Products.CMFCore.CMFCorePermissions import *

bannerManager = 'Banner manager'

ManageBanners = 'Manage banners'
setDefaultRoles(ManageBanners, ('Manager', bannerManager))
