## Controller Python Script "update_transform_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=transform_name, transform_status=None
##title=

if transform_status:
    context.portal_ploneboard.updateTransform(transform_name, transform_status=1)
else:
    context.portal_ploneboard.updateTransform(transform_name, transform_status=0)

# Optionally set the default next action (this can be overridden in the ZMI)
state.setNextAction('redirect_to:string:prefs_manage_transforms')

# Optionally pass a message to display to the user
state.setKwargs( {'portal_status_message':'Transform %s updated.' % transform_name} )

return state