from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFPhotoAlbum import PhotoAlbum, photoalbum_globals
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
import string

def install(self):
    """ """

    out = StringIO()
    typesTool = getToolByName(self, 'portal_types')
    skinsTool = getToolByName(self, 'portal_skins')

    for f in (PhotoAlbum.factory_type_information, ):
        if f['id'] not in typesTool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), f)
            typesTool._setObject(f['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                f['id']))

    if 'photoalbum_content' not in skinsTool.objectIds():
        addDirectoryViews(skinsTool, 'skins', photoalbum_globals)
        out.write("Added 'photoalbum_content' directory views to portal_skins\n")

    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'photoalbum_content' not in path and skin.startswith('Plone'):
            path.append('photoalbum_content')
            path.append('photoalbum_scripts')

            path = string.join(path, ', ')
            skinsTool.addSkinSelection(skin, path)
            out.write("Added 'photoalbum_content' to %s skins\n" % skin)
        else:
            out.write('Skipping %s skin\n' % skin)

    portal_prop=getToolByName(self, 'portal_properties')
    nav=portal_prop.navigation_properties

    site_props = getToolByName(self, 'portal_properties').site_properties
    use_folder_tabs = site_props.getProperty('use_folder_tabs')
    site_props._updateProperty('use_folder_tabs', tuple(use_folder_tabs) + ('Photo Album',))

#    nav.manage_addProperty('photoalbum.folder_edit_form.success','script:folder_edit','string');
#    nav.manage_addProperty('photoalbum.folder_edit_form.failure','folder_edit_form','string');
#    nav.manage_addProperty('photoalbum.folder_edit.success','url:folder_contents','string');
#    nav.manage_addProperty('photoalbum.folder_edit.failure','action:edit','string');

#    out.write('Added navigation properties.')



    return out.getvalue()
