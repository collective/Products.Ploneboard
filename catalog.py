from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zope.app.component.interface import interfaceToName
from zope.interface import providedBy

# Use extensible object wrapper to always list the interfaces
def object_implements(object, portal, **kw):
    return [interfaceToName(portal, i) for i in providedBy(object).flattened()]

registerIndexableAttribute('object_implements', object_implements)
