## Controller Python Script "register_schemata"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id, password=None
##title=Registration formset support
##
# handle navigation for multi-page edit forms
# copied from Archetypes' content_edit.cpy with
# minor changes to work with the join machinery
REQUEST = context.REQUEST

new_context = context.portal_factory.doCreate(context, id)
new_context.processForm()

next = not REQUEST.get('form.button.next',None) is None
previous = not REQUEST.get('form.button.previous',None) is None

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
                         portal_status_message="Content changes saved")

if next_schemata == None:
    raise 'Unable to find next field set after %s' % fieldset
