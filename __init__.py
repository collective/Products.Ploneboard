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
$Id: __init__.py,v 1.11 2004/02/16 18:21:37 dtremea Exp $
'''.strip()

from OFS.Application import get_products
from AccessControl import ModuleSecurityInfo, allow_module
from AccessControl.Permissions import view
import PatchStringIO # patch at first
from PlacelessTranslationService import PlacelessTranslationService, PTSWrapper
from utils import log
import zLOG
from Negotiator import negotiator, setSessionLanguage
from Products.PageTemplates.GlobalTranslationService import setGlobalTranslationService, getGlobalTranslationService
import os, fnmatch, sys, Zope, Globals, TranslateTags

# in python 2.1 fnmatch doesn't have the filter function
if not hasattr(fnmatch, 'filter'):
    def fnfilter(names, pattern):
        return [name for name in names if fnmatch.fnmatch(name, pattern)]
    fnmatch.filter = fnfilter

# this is for packages that need to initialize stuff after we're done
notify_initialized = []

# id to use in the Control Panel
cp_id = 'TranslationService'

# module level translation service
translation_service = None

# icon
misc_ = {
    'PlacelessTranslationService.png':
    Globals.ImageFile('www/PlacelessTranslationService.png', globals()),
    'GettextMessageCatalog.png':
    Globals.ImageFile('www/GettextMessageCatalog.png', globals()),
    }

# set product-wide attrs for importing
security = ModuleSecurityInfo('Products.PlacelessTranslationService')
allow_module('Products.PlacelessTranslationService')
allow_module('Products.PlacelessTranslationService.MessageID')

security.declareProtected(view, 'getTranslationService')
def getTranslationService():
    """ returns the PTS instance """
    #return getGlobalTranslationService()
    return translation_service

security.declareProtected(view, 'translate')
def translate(*args, **kwargs):
    """ see PlaceslessTranslationService.PlaceslessTranslationService """
    return getTranslationService().translate(*args, **kwargs)

security.declareProtected(view, 'utranslate')
def utranslate(*args, **kwargs):
    """ see PlaceslessTranslationService.PlaceslessTranslationService """
    return getTranslationService().utranslate(*args, **kwargs)

security.declareProtected(view, 'getLanguages')
def getLanguages(*args, **kwargs):
    """ see PlaceslessTranslationService.PlaceslessTranslationService """
    return getTranslationService().getLanguages(*args, **kwargs)

security.declareProtected(view, 'getLanguageName')
def getLanguageName(*args, **kwargs):
    """ see PlaceslessTranslationService.PTSWrapper """
    return getTranslationService().getLanguageName(*args, **kwargs)

security.declareProtected(view, 'setSessionLanguage')
# imported from the Negotiator

negotiateDeprecatedLogged = 0
security.declareProtected(view, 'negotiate')
def negotiate(langs, context):
    """ deprecated! """
    if not negotiateDeprecatedLogged:
        log('Products.PlacelessTranslationService.negotiate() is deprecated', zLOG.WARNING)
        negotiateDeprecatedLogged = 1
    return negotiator.negotiate(langs, context, 'language')

def make_translation_service(cp):
    """Control_Panel translation service
    """
    global translation_service
    translation_service = PlacelessTranslationService('default')
    translation_service.id = cp_id
    cp._setObject(cp_id, translation_service)
    return getattr(cp, cp_id)

def initialize(context):
    # hook into the Control Panel
    global translation_service
    cp = context._ProductContext__app.Control_Panel # argh
    if cp_id in cp.objectIds():
        cp_ts = getattr(cp, cp_id)
        # use the ts in the acquisition context of the control panel
        #translation_service = translation_service.__of__(cp)
        translation_service = cp_ts
    else:
        cp_ts = make_translation_service(cp)

    # don't touch - this is the last version that didn't have the attribute (0.4)
    instance_version = getattr(cp_ts, '_instance_version', (0, 4, 0, 0))
    if instance_version[3] > 99:
        log('development mode: translation service recreated',
            detail = '(found %s.%s.%s.%s)\n' % instance_version)
        cp._delObject(cp_id)
        cp_ts = make_translation_service(cp)
        
    if instance_version < PlacelessTranslationService._class_version:
        log('outdated translation service found, recreating',
            detail = '(found %s.%s.%s.%s)\n' % instance_version)
        cp._delObject(cp_id)
        cp_ts = make_translation_service(cp)


    # sweep products
    log('products: %r' % get_products(), zLOG.BLATHER)
    ploneDir = None
    for prod in get_products():
        # prod is a tuple in the form:
        #(priority, dir_name, index, base_dir) for each Product directory
        cp_ts._load_i18n_dir(os.path.join(prod[3], prod[1], 'i18n'))
        cp_ts._load_locales_dir(os.path.join(prod[3], prod[1], 'locales'))

    # sweep the i18n directory for local catalogs
    instance_i18n = os.path.join(INSTANCE_HOME, 'i18n')
    if os.path.isdir(instance_i18n):
        cp_ts._load_i18n_dir(instance_i18n)
        
    # didn't found any catalogs
    if not cp_ts.objectIds():
        log('no translations found!', zLOG.PROBLEM)

    # set ZPT's translation service
    # NOTE: since this registry is a global var we cant register the persistent service itself (zodb connection)
    #       therefor a wrapper is created around it
    setGlobalTranslationService(PTSWrapper(cp_ts))

    # notify anyone who needs it
    TranslateTags.initialize()
    for function in notify_initialized:
        function()
