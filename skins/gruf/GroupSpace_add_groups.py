## Script (Python) "GroupSpace_add_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member_ids=[]
##title=
##


# Add groups
for member_id in member_ids:
    context.addGroupMember(member_id)


# Redirect
context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/GroupSpace_membersForm")



