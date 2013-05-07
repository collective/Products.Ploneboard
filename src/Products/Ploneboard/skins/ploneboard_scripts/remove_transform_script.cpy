## Controller Python Script "remove_transform_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=transform_name
##title=

from Products.Ploneboard.utils import PloneboardMessageFactory as _
from Products.CMFCore.utils import getToolByName

putils = getToolByName(context, 'plone_utils')

context.portal_ploneboard.unregisterTransform(transform_name)

# Optionally set the default next action (this can be overridden in the ZMI)
state.setNextAction('redirect_to:string:prefs_manage_transforms')

# Optionally pass a message to display to the user
message = _(u'Transform %s removed') % unicode(transform_name)
putils.addPortalMessage(message)

return state

