## Script (Python) "contentpanels_edit_property"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='', title=None, description=None, customCSS='', pageLayoutMode='tile', portletsPos='none'
##

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.edit(customCSS, pageLayoutMode)

folder = context.aq_parent
slot_name = context.getPortletsPos()
if slot_name != portletsPos or id != context.getId():
    old_portlet_name = 'here/%s/contentpanels_body' % context.getId()
    new_portlet_name = 'here/%s/contentpanels_body' % id
    if slot_name != 'none':
        portlets = getattr(folder, slot_name)
        if len(portlets) == 1:
            folder.manage_delProperties([slot_name])
        new_portlets = [portlet for portlet in portlets if portlet != old_portlet_name] 
        folder.manage_changeProperties(slot_name=new_portlets)

    if portletsPos != 'none':
        if not folder.hasProperty(portletsPos):
            folder.manage_addProperty(portletsPos, [new_portlet_name], 'lines')
        else:
            portlets = folder.getProperty(portletsPos)
            portlets = [new_portlet_name] + list(portlets)
            folder.manage_changeProperties(portletsPos=portlets)

new_context.plone_utils.contentEdit(new_context
                               , id=id
                               , title=title
                               , description=description)
return state.set(status='success',\
                 context=new_context,\
                 portal_status_message='contentpanels property changes saved.')
