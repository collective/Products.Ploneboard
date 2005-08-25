## Script (Python) "getSortedConversations"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=conversations
##title=
##
# Return sorted sequence of conversations such that 'sticky' ones are first.
# Also sort on last comment datetime

wf_tool = container.portal_workflow
STICKY_STATES = ['sticky', 'locked_and_sticky']

def getState(ob):
    return wf_tool.getInfoFor(ob, 'review_state')

def stateAndDateSort(ob1, ob2):
    state1 = getState(ob1)
    state2 = getState(ob2)
    if state1 in STICKY_STATES and state2 in STICKY_STATES:
        return cmp(ob2.getLastCommentDate(), ob1.getLastCommentDate())
    elif state1 in STICKY_STATES:
        return -1
    elif state2 in STICKY_STATES:
        return 1
    return cmp(ob2.getLastCommentDate(), ob1.getLastCommentDate())

conversations.sort(stateAndDateSort)
return conversations