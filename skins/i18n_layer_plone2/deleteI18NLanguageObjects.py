## Controller Python Script "deleteI18NLanguageObjects"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a i18NLayer
##

from Products.CMFPlone import transaction_note
request = context.REQUEST

ids=request.get('ids', None)
i18n_container = context.getParentNode()

if ids:
    transaction_note( str(ids)+' has been deleted' )
    i18n_container.manage_delObjects(ids, request)
    folder_contents = i18n_container.getFolderContents()

    if folder_contents:
        object = getattr(i18n_container, folder_contents[0].getId())
        return request.RESPONSE.redirect(object.absolute_url() + '/i18n_languages_edit_form?portal_status_message=Deleted.')
    else:
        folder_container = i18n_container.getParentNode()
        folder_container.manage_delObjects([i18n_container.getId()], REQUEST)
        return request.RESPONSE.redirect(folder_container.absolute_url() + '/view?portal_status_message=Deleted.')
else:
    return request.RESPONSE.redirect(context.absolute_url() + '/i18n_languages_edit_form?portal_status_message=Please+select+one+or+more+items+first.')

