from App.Common import package_home
from Products.Archetypes.public import *
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes import listTypes
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName, minimalpath
from Products.CMFCore.DirectoryView import addDirectoryViews, createDirectoryView
from Products.I18NLayer import pt_globals as skins_globals
import string

PKG_NAME = "I18NLayer"
    
def install(self):
    out=StringIO()

    if not hasattr(self, "_isPortalRoot"):
        print >> out, "Must be installed in a CMF Site (read Plone)"
        return
    
    print >> out, "Installing %s" % listTypes(PKG_NAME)
        
    installTypes(self, out, listTypes(PKG_NAME), PKG_NAME)

    install_subskin(self, out, skins_globals)

    print >> out, 'Successfully installed types.'

    # allow content types to be added inside an i18nlayer
    typestool = getToolByName(self, 'portal_types')
    ti = typestool.getTypeInfo('I18NLayer')
    ti._setPropValue('title','I18NLayer')
    if ti:
        if ti.filter_content_types:
            for tc in typestool.objectValues():
                t=tc.getId()
                print >> out, "found type %s" % t
                if t in ('I18NLayer', 'Discussion Item', 'Favorite',): continue
                if t.lower().find('folder') > -1: continue
 
                if t in ti.allowed_content_types:
                    print >> out, '%s already allowed to be added inside I18NLayers.\n' % t
                else:
                    allowed=ti.allowed_content_types
                    if type(allowed) == type((1,)):
                        l=ti.allowed_content_types+(t,)
                    elif type(allowed) == type([1,]):
                        l=ti.allowed_content_types+[t,]
                    ti.allowed_content_types=l
                    print >> out, 'Added %s to I18NLayers allowed Content Types.\n' % t

    catalogtool = getToolByName(self, 'portal_catalog')
    # add lanugage index and column to catalog
    try: 
        catalogtool.addIndex('i18nContent_language', 'FieldIndex', 'neutral')
        print >> out, 'Added i18nContent_language to portal catalogs indexes.\n'
        catalogtool.reindexIndex('i18nContent_language', None)
        print >> out, 'Reindexed i18nContent_language index.\n'
    except: pass 
    try: 
	catalogtool.addColumn('i18nContent_language')
        print >> out, 'Added i18nContent_language to portal catalogs columns.\n'
    except: pass
    return out.getvalue()

