import sysfrom StringIO import StringIOfrom Products.Archetypes.public import listTypesfrom Products.Archetypes.Extensions.utils import installTypes, install_subskinfrom Products.CMFCore.utils import getToolByNamefrom Products.CMFPlone.migrations.migration_util import cleanupSkinPath, safeEditProperty
from Products.StandardCacheManagers import RAMCacheManager
from Products.ATAmazon.config import PROJECT_NAMEimport Products.ATAmazon as ATAmazon# TYPE_NAME = 'AmazonItem'def installProductTypes(self, out):    installTypes(self, out, listTypes(PROJECT_NAME), PROJECT_NAME)def installSkins(self, out):    skins_tool = getToolByName(self, 'portal_skins')    default_skin = skins_tool.getDefaultSkin()    cleanupSkinPath(self, default_skin)    # Setup the skins    install_subskin(self, out, ATAmazon.GLOBALS, 'skins')def installProperties(portal, out):    site_props = portal.portal_properties.site_properties
    if not hasattr(site_props, 'amazon_item_folder_id'):        safeEditProperty(site_props, 'amazon_item_folder_id', 'books', 'string')

	if not hasattr(site_props, 'amazon_developer_key'):	    safeEditProperty(site_props, 'amazon_developer_key', '', 'string')
	if not getattr(site_props, 'amazon_developer_key', ''):
	    print >> out, 'Set your Amazon web services developer key in portal_properties/site_properties/amazon_developer_key'
    if not hasattr(site_props, 'amazon_associate_id'):        safeEditProperty(site_props, 'amazon_associate_id', '', 'string')
    if not getattr(site_props, 'amazon_associate_id', ''):
        print >> out, 'Set your Amazon associate ID in portal_properties/site_properties/amazon_associate_id'    ft = getToolByName(portal, 'portal_factory')    portal_factory_types = ft.getFactoryTypes().keys()    for t in ['Amazon Item']:        if t not in portal_factory_types:            portal_factory_types.append(t)    ft.manage_setPortalFactoryTypes(listOfTypeIds=portal_factory_types)

def installCache(portal, out):
    cache_id = 'portlet_amazon_cache'
    meta_type = RAMCacheManager.RAMCacheManager.meta_type
    if cache_id not in portal.objectIds(meta_type):
        RAMCacheManager.manage_addRAMCacheManager(portal, cache_id)
        cache = getattr(portal, cache_id)
        settings = cache.getSettings()
        settings['max_age'] = 3600*24  # keep for up to 24 hours
        request_vars = ('URL0')
        cache.manage_editProps('Cache for Amazon portlet items', settings)
        # associate getAmazonItems script with cache manager
        cache.ZCacheManager_setAssociations(props={'associate_portal_skins/at_amazon/getAmazonItems':1})
    
    def install(self):    out=StringIO()    installProductTypes(self, out)    installSkins(self, out)    installProperties(self, out)
    installCache(self, out)        print >> out, 'Successfully installed %s' % PROJECT_NAME    sys.stdout.write(out.getvalue())        return out.getvalue()