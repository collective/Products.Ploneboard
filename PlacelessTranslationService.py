##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Placeless Translation Service for providing I18n to file-based code.

$Id: PlacelessTranslationService.py,v 1.2 2003/01/02 19:58:48 lalo Exp $
"""

from Negotiator import negotiator
from SimpleTranslationService import SimpleTranslationService

# The configure.zcml file should specify a list of fallback languages for the
# site.  If a particular catalog for a negotiated language is not available,
# then the zcml specified order should be tried.  If that fails, then as a
# last resort the languages in the following list are tried.  If these fail
# too, then the msgid is returned.
#
# Note that these fallbacks are used only to find a catalog.  If a particular
# message in a catalog is not translated, tough luck, you get the msgid.
LANGUAGE_FALLBACKS = ['en']


class PlacelessTranslationService(SimpleTranslationService):

    def __init__(self, default_domain='global', fallbacks=None):
        # XXX We haven't specified that ITranslationServices have a default
        # domain.  So far, we've required the domain argument to .translate()
        self._domain = default_domain
        # _catalogs maps (language, domain) to IMessageCatalog instances
        self._catalogs = {}
        # _data maps IMessageCatalog.getIdentifier() to IMessageCatalog
        self._data = {}
        # What languages to fallback to, if there is no catalog for the
        # requested language (no fallback on individual messages)
        if fallbacks is None:
            fallbacks = LANGUAGE_FALLBACKS
        self._fallbacks = fallbacks

    def _registerMessageCatalog(self, language, domain, catalog_name):
        http_language = language.lower().replace('_', '-')
        key = (http_language, domain)
        mc = self._catalogs.setdefault(key, [])
        mc.append(catalog_name)
        print 'adding catalog for domain %s, language %s' % (domain, language)

    def addCatalog(self, catalog):
        self._data[catalog.getIdentifier()] = catalog
        self._registerMessageCatalog(catalog.getLanguage(),
                                     catalog.getDomain(),
                                     catalog.getIdentifier())

    def setLanguageFallbacks(self, fallbacks=None):
        if fallbacks is None:
            fallbacks = LANGUAGE_FALLBACKS
        self._fallbacks = fallbacks


    def getLanguages(self, domain=None):
        """Get available languages"""
        if domain is not None:
            return [m[0] for m in self._catalogs.keys() if m[1] == domain]
        # no domain, so user wants 'em all
        langs = [m[0] for m in self._catalogs.keys()]
        # uniquify
        d = {}
        for l in langs:
            d[l] = 1
        return d.keys()


    def translate(self, domain, msgid, mapping=None, context=None,  
                  target_language=None, default=None):
        """
        """

        if not msgid:
            # refuse to translate an empty msgid
            return default or msgid
        
        if target_language is None:
            if context is None:
                raise TypeError, 'No destination language'
            else:
                langs = [m[0] for m in self._catalogs.keys() if m[1] == domain]
                target_language = negotiator.getLanguage(langs, context)


        # Get the translation. Use the specified fallbacks if this fails
        catalog_names = self._catalogs.get((target_language, domain), ())
        if not catalog_names:
            for language in self._fallbacks:
                catalog_names = self._catalogs.get((language, domain),  ())
                if catalog_names:
                    break
        
        for name in catalog_names:
            catalog = self._data[name]
            try:
                text = catalog.queryMessage(msgid, default)
                break
            except KeyError:
                # it's not in this catalog, try the next one
                pass
        else:
            # Did the fallback fail?  Sigh, use the default or msgid
            if default is None:
                text = msgid
            else:
                text = default

        # Now we need to do the interpolation
        text = self.interpolate(text, mapping)
        return text

    #
    ############################################################
