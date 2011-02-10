from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary

class AvailableTransformsVocabulary(object):
    """Vocabulary for available Ploneboard transforms.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context=getattr(context, "context", context)
        tool=getToolByName(context, "portal_ploneboard")
        items=[(t,t) for t in tool.getTransforms()]
        items.sort()
        return SimpleVocabulary.fromItems(items)

AvailableTransformsVocabularyFactory=AvailableTransformsVocabulary()

