## Script (Python) "mpoll_vote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Vote
##

from DateTime import DateTime

REQUEST=context.REQUEST
RESPONSE = context.REQUEST.RESPONSE

if context.isOpen():

    if REQUEST.cookies.get(context.UID()):
        return ('failure', context, {'portal_status_message': 'You have already voted in this poll.'})

    context.vote(REQUEST.answer)
    e = (DateTime('GMT') + 365).rfc822()
    RESPONSE.setCookie(context.UID(), str(REQUEST.answer), path='/', expires=e)
else:
    return ('failure', context, {'portal_status_message': 'This poll is closed.'})

return ('success', context, {'portal_status_message': 'Your vote has been registered.'})
