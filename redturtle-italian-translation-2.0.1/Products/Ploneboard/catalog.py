from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.Ploneboard.interfaces import IConversation

def num_comments(object, portal, **kw):
    conv = IConversation(object, None)
    if conv is None:
        return None
    else:
        return conv.getNumberOfComments()

registerIndexableAttribute('num_comments', num_comments)
