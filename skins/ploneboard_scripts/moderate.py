## Script (Python) "moderate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=path, workflow_action
##title=Change state of content
##

# This is used via XMLRPC for quick approval or rejection of Ploneboard posts

portal_workflow=context.portal_workflow

contentObject=context.restrictedTraverse(path)

current_state=portal_workflow.getInfoFor(contentObject, 'review_state')

try:
    if workflow_action!=current_state:
        context.portal_workflow.doActionFor( contentObject
                                           , workflow_action )
        return 1
except:
    pass

return 0
