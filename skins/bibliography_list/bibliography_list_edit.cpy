## Script (Python) "author_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=references=None, delReferences=None
##title=TTW Authors handler
##

add_button = context.REQUEST.get('form.button.reference_add',None)
del_button = context.REQUEST.get('form.button.reference_delete',None)
up_button = context.REQUEST.get('form.button.reference_up',None)
down_button = context.REQUEST.get('form.button.reference_down',None)

if add_button:
    if references is not None:
        newUID = [x for x in references]

        val = context.getReferences_list()
        val.extend(newUID)
        context.setReferences_list(val)

        return state.set(portal_status_message='Selected references added.')
    else:
        return state.set(portal_status_message='No references selected.')

if del_button:
    archetype_tool = context.archetype_tool

    if delReferences is not None:
        uids = context.getReferences_list() or []
        obs = [archetype_tool.getObject(x) for x in uids]

        obs = [x.UID() for x in obs if x.getId() not in delReferences]

        context.setReferences_list(obs)

        return state.set(portal_status_message='Selected references removed.')
    else:
        return state.set(portal_status_message='No reference selected.')

if up_button:
    archetype_tool = context.archetype_tool

    if delReferences is not None:
        uids = context.getReferences_list() or []
        obs = [archetype_tool.getObject(x) for x in uids]

        first = 1
	for x in range(len(obs)):
	    if not first and obs[x].getId() in delReferences:
	        obs[x], obs[x-1] = obs[x-1], obs[x]
	    elif first and obs[x].getId() not in delReferences:
	        first = 0

        obs = [x.UID() for x in obs]
        context.setReferences_list(obs)

        return state.set(portal_status_message='Selected references moved up.')
    else:
        return state.set(portal_status_message='No reference selected.')

if down_button:
    archetype_tool = context.archetype_tool

    if delReferences is not None:
        uids = context.getReferences_list() or []
        obs = [archetype_tool.getObject(x) for x in uids]

        first = 1
        for x in range(len(obs)):
            if not first and obs[-1-x].getId() in delReferences:
                obs[-1-x], obs[-x] = obs[-x], obs[-1-x]
            elif first and obs[-1-x].getId() not in delReferences:
                first = 0

        obs = [x.UID() for x in obs]
        context.setReferences_list(obs)

        return state.set(portal_status_message='Selected references moved down.')
    else:
        return state.set(portal_status_message='No reference selected.')
