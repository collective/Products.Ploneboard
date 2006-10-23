from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.Ploneboard.interfaces import IConversation
from zope.interface import providedBy
try:
    from zope.component.interface import interfaceToName
except ImportError:
    # BBB for Zope < 2.9
    def interfaceToName(context, interface):
        return interface.__module__ + '.' + interface.__name__

# Use extensible object wrapper to always list the interfaces
def object_implements(object, portal, **kw):
    return [interfaceToName(portal, i) for i in providedBy(object).flattened()]

registerIndexableAttribute('object_implements', object_implements)

def num_comments(object, portal, **kw):
    conv = IConversation(object, None)
    if conv is None:
        return None
    else:
        return conv.getNumberOfComments()

registerIndexableAttribute('num_comments', num_comments)
