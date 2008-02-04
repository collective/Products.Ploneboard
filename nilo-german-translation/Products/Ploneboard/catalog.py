from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.Ploneboard.interfaces import IConversation
from zope.interface import providedBy
from zope.component.interface import interfaceToName

try:
    from Products.CMFPlone.CatalogTool import object_provides
except ImportError:
    def object_provides(object, portal, **kw):
        return [interfaceToName(portal, i) for i in
                providedBy(object).flattened()]

    registerIndexableAttribute('object_provides', object_provides)


def num_comments(object, portal, **kw):
    conv = IConversation(object, None)
    if conv is None:
        return None
    else:
        return conv.getNumberOfComments()

registerIndexableAttribute('num_comments', num_comments)
