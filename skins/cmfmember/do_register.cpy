## Script (Python) "do_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id, password=None
##title=Registered
##
#next lines pulled from Archetypes' content_edit.cpy
REQUEST = context.REQUEST

new_context = context.portal_factory.doCreate(context, id)
new_context.processForm()

# XXX can't get past permission probs to get this to work
# userCreated = context.hasUser()

portal = new_context.portal_url.getPortalObject()
state.setContext(portal)

# handle navigation for multi-page edit forms
# copied from Archetypes' content_edit.cpy with
# minor changes to work with the join machinery
next = not REQUEST.get('form_next',None) is None
previous = not REQUEST.get('form_previous',None) is None
if next or previous:
    fieldset = REQUEST.get('fieldset', None)

    schematas = [s for s in new_context.Schemata().keys() if s != 'metadata']

    if previous:
        schematas.reverse()

    next_schemata = None
    try:
        index = schematas.index(fieldset)
    except ValueError:
        raise 'Non-existing fieldset: %s' % fieldset
    else:
        index += 1
        if index < len(schematas):
            next_schemata = schematas[index]
            return state.set(status='next_schemata',
                             context=new_context,
                             fieldset=next_schemata,
                             username=id, password=password,
                             portal_status_message="Your changes have been saved")

    if next_schemata == None:
        raise 'Unable to find next field set after %s' % fieldset

# XXX can't get past permission probs to get this to work
# if userCreated:
#     state.set(portal_status_message='You have been registered.',
#               id=id,
#               password=password)
# else:
#     state.set(status='pending',
#               portal_status_message='Your registration request has been received')

state.set(portal_status_message='You have been registered.',
          id=id,
          password=password)
return state
