## Script (Python) "author_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=references=None, modReferences=None
##title=TTW Authors handler
##

add_button = context.REQUEST.get('form.button.reference_add',None)
del_button = context.REQUEST.get('form.button.reference_delete',None)
up_button = context.REQUEST.get('form.button.reference_up',None)
down_button = context.REQUEST.get('form.button.reference_down',None)
sort_button = context.REQUEST.get('form.button.reference_sort',None)

field = context.getField('references_list')
uids = getattr(context, field.edit_accessor)()

if add_button:

    if references is not None:
        newUID = [x for x in references]
        uids.extend(newUID)
        context.setReferences_list(uids)
        return state.set(portal_status_message='Selected references added.')

    else:
        return state.set(portal_status_message='No references selected.')

if del_button:

    if modReferences is not None:

        uids = [x for x in uids if x not in modReferences]

        context.setReferences_list(uids)

        return state.set(portal_status_message='Selected references removed.')
    else:
        return state.set(portal_status_message='No reference selected.')

if up_button:

    if modReferences is not None:
        new_uids = [uid for uid in uids]
        idxs = [new_uids.index(ref) for ref in modReferences]
        for idx in idxs:
            idx2 = idx-1
            if idx2 < 0:
                # Wrap to the bottom.
                idx2 = len(new_uids) - 1
            # Swap.
            a = new_uids[idx2]
            new_uids[idx2] = new_uids[idx]
            new_uids[idx] = a

        context.setReferences_list(new_uids)

        return state.set(portal_status_message='Selected references moved up.')
    else:
        return state.set(portal_status_message='No reference selected.')

if down_button:

    if modReferences is not None:
        for x in range(len(uids)-1):
            if uids[x] in modReferences:
                uids[x], uids[x+1] = uids[x+1], uids[x]

        context.setReferences_list(uids)

        return state.set(portal_status_message='Selected references moved down.')
    else:
        return state.set(portal_status_message='No reference selected.')

archetype_tool = context.archetype_tool

if sort_button:

    if modReferences is not None:
        uids = context.getReferences_list() or []
        obs = [archetype_tool.lookupObject(uid) for uid in uids]
        sort_on=()
        # sort key3_sort
        for key in sortlist:
            if key== 'publication_year': sort_on.append(('publication_year', 'cmp', 'desc'))
            if key== 'Authors': sort_on.append(('Authors', 'nocase', 'asc'))
            if key== 'Source': sort_on.append(('Source', 'nocase', 'asc'))
        
        obs = sequence.sort(obs, sort_on);
        
        first = 1
        for x in range(len(obs)):
            if not first and obs[-1-x].getId() in modReferences:
                obs[-1-x], obs[-x] = obs[-x], obs[-1-x]
            elif first and obs[-1-x].getId() not in modReferences:
                first = 0
        
        obs = [x.UID() for x in obs]
        context.setReferences_list(obs)
        
        return state.set(portal_status_message='Selected references moved down.')
    else:
        return state.set(portal_status_message='No reference selected.')
