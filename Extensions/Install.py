from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFPhoto import Photo, photo_globals
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
import string

def install(self):
    """ """

    out = StringIO()
    typesTool = getToolByName(self, 'portal_types')
    skinsTool = getToolByName(self, 'portal_skins')

    for f in (Photo.factory_type_information, ):
        if f['id'] not in typesTool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), f)
            typesTool._setObject(f['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                f['id']))

##    if 'photo_content' not in skinsTool.objectIds():
##        addDirectoryViews(skinsTool, 'skins', photo_globals)
##        out.write("Added 'photo_content' directory views to portal_skins\n")

##    skins = skinsTool.getSkinSelections()
##    for skin in skins:
##        path = skinsTool.getSkinPath(skin)
##        path = map(string.strip, string.split(path,','))
##        if 'photo_content' not in path and skin.startswith('Plone'):
##            path.append('photo_content')

##            path = string.join(path, ', ')
##            skinsTool.addSkinSelection(skin, path)
##            out.write("Added 'photo_content' to %s skins\n" % skin)
##        else:
##            out.write('Skipping %s skin\n' % skin)

    portal_prop=getToolByName(self, 'portal_properties')
    nav=portal_prop.navigation_properties

    #out.write('Added navigation properties.')

    return out.getvalue()
