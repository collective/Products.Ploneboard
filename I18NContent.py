# Copyright (C) 2003 strukturAG <simon@struktur.de>
#                    http://www.strukturag.com, http://www.icoya.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Multilingual content base classes and helpers.

$Id: I18NContent.py,v 1.7 2003/10/02 14:08:10 longsleep Exp $
"""

__version__ = "$Revision: 1.7 $"

from Globals import get_request
from Acquisition import aq_acquire, aq_base, aq_inner, aq_chain, aq_parent, ImplicitAcquisitionWrapper
from Products.CMFCore.utils import _verifyActionPermissions, _checkPermission, getToolByName
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents, ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG

from utils import getLangPrefsMethod, CheckValidity


class I18NContentBase:
    """ base class for multilingual content """

    def __init__(self, layer, REQUEST, verifypermission=1):

        self.layer=layer
        if not hasattr(REQUEST, 'set'): REQUEST=get_request()
        self.REQUEST=REQUEST

        available_languages=self.getFilteredLanguageMap(verifypermission=verifypermission).keys()
        self.languages=self.getLanguagesFromRequest() + list(available_languages)
        #print "self.languages", self.languages

    def Layer(self):
        return self.layer

    def Languages(self):
        return self.languages

    def getLanguagesFromRequest(self):
        """ return a list of languages matching this request """

        REQUEST = get_request()
        language=REQUEST.cookies.get('I18N_CONTENT_LANGUAGE', None)
        language_once=REQUEST.get('cl', None)
        if not language_once:
            # we support a property here to make it possible to pre select default languages
            # for certain folders
            language_once=getattr(self.Layer(), 'local_default_language', None)
            if language_once: self.REQUEST.set('cl', language_once)
        accept=self.getLanguagesFromTranslationService()
        try: default_language=self.Layer().portal_properties.site_properties.default_language
        except: default_language=None

        #print "accept", accept, language, language_once, default_language
        languages=accept
        #print "accept", accept
        #print "language", language
        #print "language_once", language_once
        #print "default_language", default_language
        if language: languages=[language,]+languages
        if language_once and language_once != language: languages=[language_once,]+languages
        if default_language: languages=languages+[default_language,]

        #print "languages", languages
        return languages

    def getLanguagesFromTranslationService(self):
        return getLangPrefsMethod(self.REQUEST)

    def getObject(self, verifypermission=1):
        # returns the object holding language information
        # for language self.language

        # ovewrite for each implementation
        raise "NotImplementedError"

    def getFilteredLanguageMap(self, verifypermission=1):
        # returns a language code to id mapping
        raise "NotImplementedError"

    def setServed(self, lang):
        # set cookies and response headers for multilingual content
        REQUEST = get_request()
        REQUEST.set('I18N_CONTENT_SERVED_LANGUAGE', lang)
        REQUEST.RESPONSE.setHeader('Content-Language', lang)
        REQUEST.RESPONSE.setHeader('Vary', '*') #
        self.served_language=lang

    def Served(self):
        try: return self.served_language
        except: return None

    def existingLanguages(self, both=0):
        # return existing languages and existing languages name
        existing_languages=()
        existing_languages_long=()
        for code, name in self.Layer().availableLanguages():
            existing_languages=existing_languages+(code,)
            existing_languages_long=existing_languages_long+(name,)
        if not both: return existing_languages
        else: return existing_languages, existing_languages_long


class I18NContentLayer(I18NContentBase):
    """ zodb layer like content .. using seperate objects to store the different languages """

    def getFilteredLanguageMap(self, verifypermission=1):
        # filter unaccessable language objects
        # which are not accessable by the current user

        layer=self.Layer()
        try: available_languages, available_languages_long =self.existingLanguages(both=1)
        except: available_languages = available_languages_long = ()
        available_languages=list(available_languages)
        objs={}
        # use objectmanager trick to find subobjects *very* fast
        # NOTE: usually there should be much less objects inside an I18NLayer
        #       than there are existing languages
        
        pec=[layer.ContainmentContentType(),]

        # create language validator
        checker=CheckValidity(available_languages, available_languages_long)

        # XXX: this does not work for images which spec is Image
        #print "spec", spec
        #print "ids", layer.objectIds()
        #print "ids2", layer.objectIds(spec=spec)

        for id in layer.objectIds():
            if checker.check(id):
                ob = getattr(layer, id)
                if _checkPermission(View, ob) or not verifypermission:
                    name = checker.name(id)
                    objs.update({id: name})

        return objs

    def getObject(self, verifypermission=1):
        # get an object by checking until one was found

        layer=self.Layer()
        base = aq_base(layer)

        language_tool = getToolByName(layer, 'portal_languages', None)
        fallback = getattr(language_tool, 'allow_content_language_fallback', 1)        
        
        fallenback=None
        #print "fallback, verify", fallback, verifypermission
        for lang in self.Languages():
            #print "lang", lang
            if hasattr(base, lang):
                ob = getattr(layer, lang)
                #print "ob", repr(ob)
                if verifypermission: allowed = _checkPermission(View, ob)
                else: allowed = 1
                #print "allowed", allowed
    
                if allowed:
                    #print "check", self.Languages()
                    if not fallback and lang != self.Languages()[0]:
                        # we have fallen back but are not allowed to
                        fallenback=lang
                        break
                
                    else:
                        # not fallen back or allowed to
                        self.setServed(lang)
                        return ob


        if not fallback and fallenback:
            # we are fallen back but are not allowed to fall back
            return None

        if len(self.getFilteredLanguageMap(verifypermission=verifypermission).keys()):
            # we have access to at least one language but are not fallen back
            return None

        if verifypermission and not _checkPermission(ModifyPortalContent, layer):
            raise "Unauthorized", "you are not allowed to access this object"

        return None




