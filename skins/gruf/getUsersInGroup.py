## Script (Python) "getUsersInGroup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupid
##title=
##

users=context.acl_users.getUsers()
prefix=context.acl_users.getGroupPrefix()

avail=[]
for user in users:
    for group in user.getGroups():
        if groupid==group or \
           prefix+groupid==group:
            avail.append(user)

return avail
