## Controller Python Script "remove_transform_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=transform_name
##title=

context.portal_ploneboard.unregisterTransform(transform_name)

# Optionally set the default next action (this can be overridden in the ZMI)
state.setNextAction('redirect_to:string:prefs_manage_transforms')

# Optionally pass a message to display to the user
state.setKwargs( {'portal_status_message':'Transform %s removed.' % transform_name} )

return state
  
