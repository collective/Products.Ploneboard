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

if portletsPos != 'none' and id == 'index_html':
    # I found portlet doesn't work when id is 'index_html', strange.
    return state.set(status='failure',\
           portal_status_message="Short ID can't be index_html when set to left/right column.")

old_id = context.getId()
folder = context.aq_parent
oldPortletPos = context.getPortletsPos()

new_context = context.portal_factory.doCreate(context, id)

new_context.edit(customCSS, pageLayoutMode)
new_context.plone_utils.contentEdit(new_context
                               , id=id
                               , title=title
                               , description=description)
# portlet lost when rename
if id != old_id:
    oldPortletPos = 'none'

if oldPortletPos != portletsPos:
    new_portlet_name = 'here/%s/contentpanels_body' % id
    if oldPortletPos != 'none':
        portlets = getattr(folder, oldPortletPos)
        if len(portlets) == 1:
            folder.manage_delProperties([oldPortletPos])
        old_portlet_name = 'here/%s/contentpanels_body' % old_id
        new_portlets = [portlet for portlet in portlets if portlet != old_portlet_name] 
        folder.manage_changeProperties({oldPortletPos:new_portlets})

    if portletsPos != 'none':
        if not folder.hasProperty(portletsPos):
            folder.manage_addProperty(portletsPos, [new_portlet_name], 'lines')
        else:
            portlets = folder.getProperty(portletsPos)
            portlets = [new_portlet_name] + list(portlets)
            folder.manage_changeProperties({portletsPos:portlets})

return state.set(status='success',\
                 context=new_context,\
                 portal_status_message='contentpanels property changes saved.')
