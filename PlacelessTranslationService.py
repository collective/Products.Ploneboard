##############################################################################
#    Copyright (C) 2001, 2002, 2003 Lalo Martins <lalo@laranja.org>,
#                  Zope Corporation and Contributors

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
"""Placeless Translation Service for providing I18n to file-based code.

$Id: PlacelessTranslationService.py,v 1.14 2004/01/28 13:48:15 tiran Exp $
"""

import sys, re, zLOG, Globals, fnmatch
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from types import DictType, StringType, UnicodeType
from Negotiator import negotiator
from Domain import Domain
from msgfmt import PoSyntaxError
import os
try:
    from pax import XML
except:
    def XML(v):
        return str(v)
try:
    True
except NameError:
    True=1
    False=0
_marker = []

def log(msg, severity=zLOG.INFO, detail='', error=None):
    if type(msg) is UnicodeType:
        msg = msg.encode(sys.getdefaultencoding(), 'replace')
    if type(detail) is UnicodeType:
        detail = detail.encode(sys.getdefaultencoding(), 'replace')
    zLOG.LOG('PlacelessTranslationService', severity, msg, detail, error)

def map_get(map, name):
    return map.get(name)

# Setting up some regular expressions for finding interpolation variables in
# the text.
NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_interp_regex = re.compile(r'(?<!\$)(\$(?:%(n)s|{%(n)s}))' %({'n': NAME_RE}))
_get_var_regex = re.compile(r'%(n)s' %({'n': NAME_RE}))


# The configure.zcml file should specify a list of fallback languages for the
# site.  If a particular catalog for a negotiated language is not available,
# then the zcml specified order should be tried.  If that fails, then as a
# last resort the languages in the following list are tried.  If these fail
# too, then the msgid is returned.
#
# Note that these fallbacks are used only to find a catalog.  If a particular
# message in a catalog is not translated, tough luck, you get the msgid.
LANGUAGE_FALLBACKS = list(os.environ.get('LANGUAGE_FALLBACKS', 'en').split(' '))

from UserDict import UserDict

class Registry(UserDict):

    def register(self, name, value):
        self[name] = value

catalogRegistry = Registry()
registerCatalog = catalogRegistry.register
fbcatalogRegistry = Registry()
registerFBCatalog = fbcatalogRegistry.register


class PTSWrapper:
    """
    Wrap the persistent PTS since persistent 
    objects cant be passed around threads
    """

    #XXX: better have a real seperation between 
    #     control panel and translation service
    #     to avoid these zodb traversals
    
    def __init__(self, service):
        # get path from service
        self._path=service.getPhysicalPath()

    def load(self, context):
        # return the real service
        try: root = context.getPhysicalRoot()
        except: return None
        # traverse the service
        return root.unrestrictedTraverse(self._path, None)

    def translate(self, domain, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """translate a message using the default encoding
        
        get the real service and call its translate method
        return default if service couldnt be retrieved
        """
        service = self.load(context)
        if not service: return default
        return service.translate(domain, msgid, mapping, context, target_language, default)

    def utranslate(self, domain, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """translate a message using unicode
        
        see translate()
        """
        service = self.load(context)
        if not service: return default
        return service.utranslate(domain, msgid, mapping, context, target_language, default)

    def __repr__(self):
        """ return a string representation """
        return "<PTSWrapper for %s>" %(self._path)


class PlacelessTranslationService(Folder):
    """
    The Placeless Translation Service
    """

    meta_type = title = 'Placeless Translation Service'
    icon = 'misc_/PlacelessTranslationService/PlacelessTranslationService.png'
    # major, minor, patchlevel, internal
    # internal is always 0 on releases; if you hack this internally, increment it
    # -3 for alpha, -2 for beta, -1 for release candidate
    # for forked releases internal is always 99
    _class_version = (1, -2, 3, 99)
    all_meta_types = ()

    security = ClassSecurityInfo()
    security.declarePublic('translate')
    security.declarePublic('getLanguages')
    security.declarePublic('getLanguageName')

    def __init__(self, default_domain='global', fallbacks=None):
        self._instance_version = self._class_version
        # XXX We haven't specified that ITranslationServices have a default
        # domain.  So far, we've required the domain argument to .translate()
        self._domain = default_domain
        # _catalogs maps (language, domain) to identifiers
        catalogRegistry = {}
        fbcatalogRegistry = {}
        # What languages to fallback to, if there is no catalog for the
        # requested language (no fallback on individual messages)
        if fallbacks is None:
            fallbacks = LANGUAGE_FALLBACKS
        self._fallbacks = fallbacks

    def _registerMessageCatalog(self, catalog):

        from GettextMessageCatalog import BrokenMessageCatalog
        # dont register broken message catalogs
        if isinstance(catalog, BrokenMessageCatalog): return

        domain = catalog.getDomain()
        catalogRegistry.setdefault((catalog.getLanguage(), domain), []).append(catalog.getIdentifier())
        for lang in catalog.getOtherLanguages():
            fbcatalogRegistry.setdefault((lang, domain), []).append(catalog.getIdentifier())
        self._p_changed = 1

    def _unregister_inner(self, catalog, clist):
        for key, combo in clist.items():
            try:
                combo.remove(catalog.getIdentifier())
            except ValueError:
                continue
            if not combo: # removed the last catalog for a language/domain combination
                del clist[key]

    def _unregisterMessageCatalog(self, catalog):
        self._unregister_inner(catalog, catalogRegistry)
        self._unregister_inner(catalog, fbcatalogRegistry)
        self._p_changed = 1

    def _load_dir(self, basepath):
        from GettextMessageCatalog import GettextMessageCatalog, BrokenMessageCatalog
        log('looking into ' + basepath, zLOG.BLATHER)
        if not os.path.isdir(basepath):
            log('it does not exist', zLOG.BLATHER)
            return

        # print deprecation warning for mo files
        depr_names = fnmatch.filter(os.listdir(basepath), '*.mo')
        if depr_names: 
            import warnings
            warnings.warn('Compiled po files (*.mo) found in %s. PlacelessTranslationService now compiles mo files automatically. All mo files have been ignored.' % basepath, DeprecationWarning, stacklevel=4)

        # load po files
        names = fnmatch.filter(os.listdir(basepath), '*.po')
        if not names:
            log('nothing found', zLOG.BLATHER)
            return
        for name in names:
            ob = self._getOb(name, _marker)
            try:
                if isinstance(ob, BrokenMessageCatalog):
                    # remove broken catalog
                    self._delObject(name)
                    ob = _marker
            except: pass
            try:
                if ob is _marker:
                    self.addCatalog(GettextMessageCatalog(os.path.join(basepath, name)))
                else:
                    self.reloadCatalog(ob)
            except IOError:
                # io error probably cause of missing or 
                # not accessable 
                try:
                    # remove false catalog from PTS instance
                    self._delObject(name)
                except:
                    pass
            except:
                 exc=sys.exc_info()
                 log('Message Catalog has errors', zLOG.PROBLEM, name, exc)
                 self.addCatalog(BrokenMessageCatalog(os.path.join(basepath, name), exc))
                 
        log('Initialized:', detail = repr(names) + (' from %s\n' % basepath))

    def manage_renameObject(self, id, new_id, REQUEST=None):
        "wrap manage_renameObject to deal with registration"
        catalog = self._getOb(id)
        self._unregisterMessageCatalog(catalog)
        Folder.manage_renameObject(self, id, new_id, REQUEST=None)
        self._registerMessageCatalog(catalog)

    def _delObject(self, id, dp=1):
        catalog = self._getOb(id)
        Folder._delObject(self, id, dp)
        self._unregisterMessageCatalog(catalog)

    def reloadCatalog(self, catalog):
        # trigger an exception if we don't know anything about it
        id=catalog.id
        self._getOb(id)
        self._unregisterMessageCatalog(catalog)
        catalog.reload()
        catalog=self._getOb(id)
        self._registerMessageCatalog(catalog)

    def addCatalog(self, catalog):
        try:
            self._delObject(catalog.id)
        except:
            pass
        self._setObject(catalog.id, catalog, set_owner=False)
        log('adding %s: %s' % (catalog.id, catalog.title))
        self._registerMessageCatalog(catalog)

    def setLanguageFallbacks(self, fallbacks=None):
        if fallbacks is None:
            fallbacks = LANGUAGE_FALLBACKS
        self._fallbacks = fallbacks

    def getLanguageName(self, code):
        for (ccode, cdomain), cnames in catalogRegistry.items():
            if ccode == code:
                for cname in cnames:
                    cat = self._getOb(cname)
                    if cat.name:
                        return cat.name

    def getLanguages(self, domain=None):
        """Get available languages"""
        if domain is None:
            # no domain, so user wants 'em all
            langs = catalogRegistry.keys()
            # uniquify
            d = {}
            for l in langs:
                d[l[0]] = 1
            l = d.keys()
        else:
            l = [k[0] for k in catalogRegistry.keys() if k[1] == domain]
        l.sort()
        return l

    def utranslate(self, domain, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """translate() using unicode
        """
        self.translate(domain, msgid, mapping, context,
                  target_language, default, as_unicode=True)

    def translate(self, domain, msgid, mapping=None, context=None,
                  target_language=None, default=None, as_unicode=False):
        """
        """
        from GettextMessageCatalog import translationRegistry, getMessage

        if not msgid:
            # refuse to translate an empty msgid
            return default

        # ZPT passes the object as context.  That's wrong according to spec.
        try:
            context = context.REQUEST
        except AttributeError:
            pass

        if target_language is None:
            target_language = self.negotiate_language(context, domain)

        # Get the translation. Use the specified fallbacks if this fails
        catalog_names = catalogRegistry.get((target_language, domain), ()) or \
                        fbcatalogRegistry.get((target_language, domain), ())
        if not catalog_names:
            for language in self._fallbacks:
                catalog_names = catalogRegistry.get((language, domain),  ())
                if catalog_names:
                    break

        for name in catalog_names:
            catalog = translationRegistry[name]
            try:
                text = getMessage(catalog, msgid, default)
            except KeyError:
                # it's not in this catalog, try the next one
                continue
            # found! negotiate output encodings now
            if hasattr(context, 'pt_output_encoding'):
                # OpenPT
                encodings = catalog._info.get('preferred-encodings', '').split()
                if encodings:
                    context.pt_output_encoding.restrict(catalog, encodings)
            elif not as_unicode:
                # ZPT probably
                # ask HTTPResponse to encode it for us
                text = context.RESPONSE._encode_unicode(text)
            break
        else:
            # Did the fallback fail?  Sigh, use the default.
            # OpenTAL provides a default text.
            # TAL doesn't but will use the default
            # if None is returned
            text = default

        # Now we need to do the interpolation
        text = self.interpolate(text, mapping)
        return text

    def negotiate_language(self, context, domain):
        if context is None:
            raise TypeError, 'No destination language'
        langs = [m[0] for m in catalogRegistry.keys() if m[1] == domain] + \
                [m[0] for m in fbcatalogRegistry.keys() if m[1] == domain]
        for fallback in self._fallbacks:
            if fallback not in langs:
                langs.append(fallback)
        return negotiator.negotiate(langs, context, 'language')

    def getDomain(self, domain):
        """
        """
        return Domain(domain, self)

    def interpolate(self, text, mapping):
     try:
        """Insert the data passed from mapping into the text"""

        # If the mapping does not exist, make a "raw translation" without
        # interpolation.
        if mapping is None or type(text) not in (StringType, UnicodeType):
            # silly wabbit!
            return text

        get = map_get
        try:
            mapping.get('')
        except AttributeError:
            get = getattr

        # Find all the spots we want to substitute
        to_replace = _interp_regex.findall(text)

        # ZPT (string) or OpenPT (unicode)?
        if type(text) is StringType:
            conv = str
        else:
            conv = XML

        # Now substitute with the variables in mapping
        for string in to_replace:
            var = _get_var_regex.findall(string)[0]
            value = get(mapping, var)
            try:
                value = value()
            except (TypeError, AttributeError):
                pass
            if value is None:
                value = string
            if type(value) not in (StringType, UnicodeType):
                # FIXME: we shouldn't do this. We should instead
                # return a list. But i'm not sure about how to use
                # the regex to split the text.
                value = conv(value)
            text = text.replace(string, value)

        return text
     except:
        import traceback
        traceback.print_exc()

    def manage_main(self, REQUEST, *a, **kw):
        "Wrap Folder's manage_main to render international characters"
        # ugh, API cruft
        if REQUEST is self and a:
            REQUEST = a[0]
            a = a[1:]
        r = Folder.manage_main(self, self, REQUEST, *a, **kw)
        if type(r) is UnicodeType:
            r = r.encode('utf-8')
        REQUEST.RESPONSE.setHeader('Content-type', 'text/html; charset=utf-8')
        return r

    #
    ############################################################
