## Controller Python Script "add_transform_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=transform_name, module_name
##title=Add transform

context.portal_ploneboard.registerTransform(transform_name, module_name)

return state