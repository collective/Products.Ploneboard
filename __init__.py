from DCWorkflowGraph import getGraph
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import os

manage_workflowGraph = PageTemplateFile(os.path.join('www','manage_workflowGraph'), globals())
manage_workflowGraph.__name__ = 'manage_workflowGraph'
manage_workflowGraph._need__name__ = 0

DCWorkflowDefinition.getGraph=getGraph
DCWorkflowDefinition.manage_workflowGraph=manage_workflowGraph
DCWorkflowDefinition.manage_options=tuple(DCWorkflowDefinition.manage_options)+({'label': 'graph', 'action': 'manage_workflowGraph'},)
