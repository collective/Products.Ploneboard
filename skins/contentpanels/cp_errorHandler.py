## Script (Python) "cp_errorHandler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFContentPanels import EmptyPanelException
error=_['error']
elif error.type == 'Unauthorized':
  return ""
else:
  raise error
