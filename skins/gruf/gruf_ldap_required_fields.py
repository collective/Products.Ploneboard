## Script (Python) "gruf_ldap_required_fields"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=login
##title=Mandatory / default LDAP attribute values
##

return {
  "sn": login,
  "cn": login,
  }
