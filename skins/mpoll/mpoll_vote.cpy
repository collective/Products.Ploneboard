## Script (Python) "mpoll_vote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Vote
##

from DateTime import DateTime

REQUEST=context.REQUEST
RESPONSE = context.REQUEST.RESPONSE

if context.isOpen():

    if REQUEST.cookies.get(context.UID()):
        return state.set(status='failure', portal_status_message='You have already voted in this poll.')

    context.vote(REQUEST.answer)
    e = (DateTime('GMT') + 365).rfc822()
    RESPONSE.setCookie(context.UID(), str(REQUEST.answer), path='/', expires=e)
else:
    return state.set(status='failure', portal_status_message='This poll is closed.')

return state.set(status="success", portal_status_message='Your vote has been registered.')
