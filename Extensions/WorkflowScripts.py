from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _mergedLocalRoles
from ZODB.POSException import ConflictError

from Products.ATContentTypes.migration.common import unrestricted_rename

from DateTime import DateTime

import re
from random import random


def autopublish_script(self, sci):
    """Publish the conversation along with the comment"""
    object = sci.object

    wftool = sci.getPortal().portal_workflow

    # Try to make sure that conversation and contained messages are in sync
    if object.portal_type == 'PloneboardComment':
        parent = object.aq_inner.aq_parent
        if parent.portal_type == 'PloneboardConversation':
            try:
                if wftool.getInfoFor(parent,'review_state',None) in (sci.old_state.getId(), 'pending'):
                    wftool.doActionFor(parent, 'make_active')
            except:
                pass

def publish_script(self, sci):
    """Publish the conversation along with comment"""
    object = sci.object

    wftool = sci.getPortal().portal_workflow

    if object.portal_type == 'PloneboardComment':
        parent = object.aq_inner.aq_parent
        if parent.portal_type == 'PloneboardConversation':
            try:
                if parent.getNumberOfMessages() == 0 and wftool.getInfoFor(parent,'review_state',None) == sci.old_state.getId():
                    wftool.doActionFor(parent, sci.transition.getId())
            except:
                pass

def reject_script(self, sci):
    """Reject conversation along with comment"""
    # Dispatch to more easily customizable methods
    object = sci.object
    # We don't have notifyPublished method anymore
    #object.notifyRetracted()

    wftool = sci.getPortal().portal_workflow

    # Try to make sure that conversation and contained messages are in sync
    if object.portal_type == 'PloneboardComment':
        parent = object.aq_inner.aq_parent
        if parent.portal_type == 'PloneboardConversation':
            try:
                if parent.getNumberOfMessages() == 0 and wftool.getInfoFor(parent,'review_state',None) == sci.old_state.getId():
                    wftool.doActionFor(parent, sci.transition.getId())
            except:
                pass


def example_script(self, sci):
    """Example, keep parent in sync with object"""
    wftool = sci.getPortal().portal_workflow
    
    parent = aq_parent(aq_inner(sci.object))
    try:
        if wftool.getInfoFor(parent,'review_state',None) in (sci.old_state.getId(), 'pending'):
            wftool.doActionFor(parent, sci.transition.getId())
    except ConflictError:
        raise
    except:
        pass
