## Script (Python) "createMember"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
from DateTime import DateTime
now=DateTime()
### XXX REAL CODE --> REMOVED FOR DEVEL ###
type_name = context.portal_memberdata.getTypeName()
#type_name = context.portal_memberdata.typeName
id=type_name.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
context.REQUEST.RESPONSE.redirect('%s/portal_memberdata/portal_factory/%s/%s/join_form' % (context.portal_url(), type_name, id))
