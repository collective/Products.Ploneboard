from Acquisition import aq_inner, aq_parent
from Products.Ploneboard.interfaces import IConversation, IComment


def autopublish_script(self, sci):
    """Publish the conversation along with the comment"""
    object = sci.object

    wftool = sci.getPortal().portal_workflow

    # Try to make sure that conversation and contained messages are in sync
    if IComment.providedBy(object):
        parent = aq_parent(aq_inner(object))
        if IConversation.providedBy(parent):
            try:
                if wftool.getInfoFor(parent,'review_state', None) in (sci.old_state.getId(), 'pending'):
                    wftool.doActionFor(parent, 'publish')
            except Exception:
                pass


def publish_script(self, sci):
    """Publish the conversation along with comment"""
    object = sci.object

    wftool = sci.getPortal().portal_workflow

    if IComment.providedBy(object):
        parent = aq_parent(aq_inner(object))
        if IConversation.providedBy(parent):
            try:
                if wftool.getInfoFor(parent,'review_state', None) in (sci.old_state.getId(), 'pending'):
                    wftool.doActionFor(parent, 'publish')
            except Exception:
                pass


def reject_script(self, sci):
    """Reject conversation along with comment"""
    # Dispatch to more easily customizable methods
    object = sci.object
    # We don't have notifyPublished method anymore
    #object.notifyRetracted()

    wftool = sci.getPortal().portal_workflow

    # Try to make sure that conversation and contained messages are in sync
    if IComment.providedBy(object):
        parent = aq_parent(aq_inner(object))
        if IConversation.providedBy(parent):
            try:
                 if wftool.getInfoFor(parent,'review_state', None) in (sci.old_state.getId(), 'pending'):
                    wftool.doActionFor(parent, 'reject')
            except Exception:
                pass


def lock_or_unlock(self, sci):
    """ locks or unlocks board """
    obj = sci.object
    if sci.old_state.id == 'locked':
        obj.unlock_board()
    elif sci.new_state.id == 'locked':
        obj.lock_board()

