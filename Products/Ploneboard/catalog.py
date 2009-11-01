from Products.Ploneboard.interfaces import IConversation

from plone.indexer.decorator import indexer
@indexer(IConversation)
def num_comments(obj):
    return obj.getNumberOfComments()
