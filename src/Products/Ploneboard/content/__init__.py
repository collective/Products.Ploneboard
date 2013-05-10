import Ploneboard
import PloneboardForum
import PloneboardConversation
import PloneboardComment

from zope import interface


try:
    from Products.CMFPlone.interfaces.syndication import ISyndicatable
except ImportError:
    ISyndicatable = None


if ISyndicatable is not None:
    for i, klass in (
        (Ploneboard, 'Ploneboard'),
        (PloneboardForum, 'PloneboardForum'),
        (PloneboardConversation, 'PloneboardConversation'),
    ):
        interface.classImplements(getattr(i, klass), ISyndicatable)
