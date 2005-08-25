## Script (Python) "genCommentModerateOnClick"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=comment, transition
##title=Generates a suitable onclick string for the comment_view comment macro
##

template = "moderateComment('%s', '%s', this, 'comment-%s');"
return template % ('/'.join(context.portal_url.getRelativeContentPath(comment)), transition.get('id'), comment.getId())