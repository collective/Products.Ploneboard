"""Event handlers for Ploneboard."""

import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.WorkflowPolicyConfig import manage_addWorkflowPolicyConfig
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id

LOG = logging.getLogger('Plone')

def onForumCreated(forum, event):
    """Subscriber for ObjectModifiedEvent"""
    if forum.getAllowEditComment() and WorkflowPolicyConfig_id not in forum.objectIds():
        manage_addWorkflowPolicyConfig(forum)
        pw_tool = getToolByName(forum, 'portal_placeful_workflow')
        config = pw_tool.getWorkflowPolicyConfig(forum)
        config.setPolicyIn(policy='EditableComment')
        config.setPolicyBelow(policy='EditableComment', update_security=True)
        LOG.info('Created workflow polify for forum %s', '/'.join(forum.getPhysicalPath()))
    elif WorkflowPolicyConfig_id in forum.objectIds() and not forum.getAllowEditComment():
        forum.manage_delObjects([WorkflowPolicyConfig_id])
        LOG.info('Deleted workflow polify for forum %s', '/'.join(forum.getPhysicalPath()))


