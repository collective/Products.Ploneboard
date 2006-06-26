## Script (Python) "moderateComment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=action,cameFrom=None
##title=Moderate the given comment, and return to referer
##

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

workflow = getToolByName(context, 'portal_workflow')
workflow.doActionFor(context, action)

if cameFrom is None:
    cameFrom = context.REQUEST.get('HTTP_REFERER', context.absolute_url())
context.REQUEST.RESPONSE.redirect(cameFrom)