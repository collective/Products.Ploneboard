##############################################################################
#    Copyright (C) 2001, 2002, 2003 Lalo Martins <lalo@laranja.org>,
#                  and Contributors

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307, USA
__version__ = '''
$Id: __init__.py,v 1.3 2003/11/20 16:14:51 tesdal Exp $
'''.strip()

from OFS.Application import get_products
from AccessControl import ModuleSecurityInfo, allow_module, allow_class, allow_type
from PlacelessTranslationService import PlacelessTranslationService, log
from Negotiator import negotiator
from Products.PageTemplates.GlobalTranslationService import setGlobalTranslationService
import os, fnmatch, zLOG, sys, Zope, Globals, TranslateTags

# in python 2.1 fnmatch doesn't have the filter function
if not hasattr(fnmatch, 'filter'):
    def fnfilter(names, pattern):
        return [name for name in names if fnmatch.fnmatch(name, pattern)]
    fnmatch.filter = fnfilter

# patch flaky ZPT - this must be removed once someone fixes it
# I'm leaving this enabled even for OpenPT, because it somehow manages
# to make zope a bit faster...
import PatchStringIO

# this is for packages that need to initialize stuff after we're done
notify_initialized = []

# id to use in the Control Panel
cp_id = 'TranslationService'

# icon
misc_ = {
    'PlacelessTranslationService.png':
    Globals.ImageFile('www/PlacelessTranslationService.png', globals()),
    'GettextMessageCatalog.png':
    Globals.ImageFile('www/GettextMessageCatalog.png', globals()),
    }

# this is the module-level translation service
translation_service = PlacelessTranslationService('default')

# set product-wide attrs for importing
translate = translation_service.translate
getLanguages = translation_service.getLanguages
getLanguageName = translation_service.getLanguageName
def negotiate(langs, context):
    # deprecated!
    return negotiator.negotiate(langs, context, 'language')

# import permissions
security = ModuleSecurityInfo('Products.PlacelessTranslationService')
security.declarePublic('negotiator')
security.declarePublic('negotiate')
security.declarePublic('translate')
security.declarePublic('getLanguages')
security.declarePublic('getLanguageName')

# set ZPT's translation service
setGlobalTranslationService(translation_service)

def make_translation_service(cp):
    # Control_Panel translation service
    translation_service = PlacelessTranslationService('default')
    translation_service.id = cp_id
    cp._setObject(cp_id, translation_service)
    return getattr(cp, cp_id)

def initialize(context):
    # hook into the Control Panel
    cp = context._ProductContext__app.Control_Panel # argh
    if cp_id in cp.objectIds():
        cp_ts = getattr(cp, cp_id)
    else:
        cp_ts = make_translation_service(cp)

    # don't touch - this is the last version that didn't have the attribute (0.4)
    instance_version = getattr(cp_ts, '_instance_version', (0, 4, 0, 0))
    if instance_version < PlacelessTranslationService._class_version:
        log('outdated translation service found, recreating',
            detail = '(found %s.%s.%s.%s)\n' % instance_version)
        cp._delObject(cp_id)
        cp_ts = make_translation_service(cp)

    # sweep products
    log('products: %r' % get_products(), zLOG.BLATHER)
    for prod in get_products():
        # prod is a tuple in the form:
        #(priority, dir_name, index, base_dir) for each Product directory
        cp_ts._load_dir(os.path.join(prod[3], prod[1], 'i18n'))

    # sweep the i18n directory for local catalogs
    cp_ts._load_dir(os.path.join(INSTANCE_HOME, 'i18n'))

    # didn't found any catalogs
    if not cp_ts.objectIds():
        log('no translations found!', zLOG.PROBLEM)

    # notify anyone who needs it
    TranslateTags.initialize()
    for function in notify_initialized:
        function()
