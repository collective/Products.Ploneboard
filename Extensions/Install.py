from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFPhoto import Photo, PhotoFolder, photo_globals
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
import string

def install(self):
    """ """

    out = StringIO()
    typesTool = getToolByName(self, 'portal_types')
    skinsTool = getToolByName(self, 'portal_skins')

    for f in (Photo.factory_type_information, PhotoFolder.factory_type_information):
        if f['id'] not in typesTool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), f)
            typesTool._setObject(f['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                f['id']))

    if 'plone_photo' not in skinsTool.objectIds():
        addDirectoryViews(skinsTool, 'skins', photo_globals)
        out.write("Added 'plone_photo' directory views to portal_skins\n")

    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'plone_photo' not in path and skin.startswith('Plone'):
            path.append('plone_photo')

            path = string.join(path, ', ')
            skinsTool.addSkinSelection(skin, path)
            out.write("Added 'plone_photo' to %s skins\n" % skin)
        else:
            out.write('Skipping %s skin\n' % skin)

#    portal_form=getToolByName(self, 'portal_form')
#    portal_form.setValidators('photo_edit_form', ['validate_id','validate_photo_edit'])

    portal_prop=getToolByName(self, 'portal_properties')
    nav=portal_prop.navigation_properties

    nav.manage_addProperty('photo.image_edit.success','action:view','string');
    nav.manage_addProperty('photo.image_edit.failure','action:edit','string');
    nav.manage_addProperty('photo.image_edit_form.success','script:image_edit','string');
    nav.manage_addProperty('photo.image_edit_form.failure','image_edit_form','string');

    nav.manage_addProperty('default.photo_settings.succes','action:view','string');
    nav.manage_addProperty('default.photo_settings.failure','action:photo_settings','string');
    nav.manage_addProperty('default.photo_settings_form.succes','script:photo_settings','string');
    nav.manage_addProperty('default.photo_settings_form.failure','photo_settings_form','string');

    nav.manage_addProperty('default.photo_rotate.succes','action:view','string');
    nav.manage_addProperty('default.photo_rotate.failure','action:photo_rotate','string');
    nav.manage_addProperty('default.photo_rotate_form.succes','script:photo_rotate','string');
    nav.manage_addProperty('default.photo_rotate_form.failure','photo_rotate_form','string');

    nav.manage_addProperty('photofolder.folder_edit_form.success','script:folder_edit','string');
    nav.manage_addProperty('photofolder.folder_edit_form.failure','folder_edit_form','string');
    nav.manage_addProperty('photofolder.folder_edit.success','action:view','string');
    nav.manage_addProperty('photofolder.folder_edit.failure','action:edit','string');

    out.write('Added navigation properties.')

    return out.getvalue()
