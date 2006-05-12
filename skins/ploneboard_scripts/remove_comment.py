## Script (Python) "remove_comment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=comment=None, redirect=1, REQUEST=None
##title=
##

if comment is None:
    comment = context

conv = comment.getConversation()
conv.removeComment(context)

REQUEST.RESPONSE.redirect("%s?portal_status_message=%s" % 
        (conv.absolute_url(), "Comment has been deleted"))

