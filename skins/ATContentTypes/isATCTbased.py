## Script (Python) "isATCTbased"
##title=Formats the history diff
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj

from Products.CMFCore.utils import getToolByName

iface = getToolByName(context, 'portal_interface')

return iface.objectImplements(obj,
           'Products.ATContentTypes.interfaces.IATContentType.IATContentType')
