## Script (Python) "do_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Prune orphans
##
context.pruneMemberDataContents()
return state.set(portal_status_message='Orphan member objects have been deleted.')
