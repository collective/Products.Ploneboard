from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zope.interface import providedBy
try:
    from zope.app.component.interface import interfaceToName
except ImportError:
    # BBB for Zope < 2.9
    def interfaceToName(context, interface):
        return interface.__module__ + '.' + interface.__name__

# Use extensible object wrapper to always list the interfaces
def object_implements(object, portal, **kw):
    return [interfaceToName(portal, i) for i in providedBy(object).flattened()]

registerIndexableAttribute('object_implements', object_implements)
