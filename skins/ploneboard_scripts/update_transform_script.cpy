## Controller Python Script "update_transform_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=transforms=[]
##title=

from Products.CMFCore.utils import getToolByName

pb_tool=getToolByName(context, 'portal_ploneboard')

for t in pb_tool.getTransforms():
    pb_tool.enableTransform(t, t in transforms)

return state
