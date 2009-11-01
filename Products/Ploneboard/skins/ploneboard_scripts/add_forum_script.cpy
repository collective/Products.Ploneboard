## Controller Python Script "add_forum_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id, title='', description=''
##title=Add a forum

context.addForum(id, title=title, description=description)

return state
