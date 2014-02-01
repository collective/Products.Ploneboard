from plone.indexer.decorator import indexer
from Products.Ploneboard.interfaces import IConversation

@indexer(IConversation)
def num_comments(obj):
    return obj.getNumberOfComments()
