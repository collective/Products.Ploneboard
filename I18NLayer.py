# Copyright (C) 2003 strukturAG <simon@struktur.de>
# http://www.strukturag.com, http://www.icoya.com

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
I18NLayer. Overlay to provide multilanguage support for all types objects.

$Id: I18NLayer.py,v 1.2 2003/03/26 11:41:53 vladoi Exp $
"""

__version__ = "$Revision: 1.2 $"

from Acquisition import aq_acquire, aq_base, aq_inner, aq_chain, aq_parent, ImplicitAcquisitionWrapper
from OFS.ObjectManager import ObjectManager
from Products.CMFCore.utils import _verifyActionPermissions, _checkPermission
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents, ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from ExtensionClass import Base
from Globals import InitializeClass
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG
from Products.Archetypes.public       import *
from Products.CMFPlone.PloneFolder import _getViewFor

# PlacelessTranslation Service Negotiator Support
try: 
    from Products.PlacelessTranslationService.Negotiator \
        import getLangPrefsMethod as pts_getLangPrefsMethod
    getLangPrefsMethod = lambda req, get=pts_getLangPrefsMethod: get(req).getPreferredLanguages()
except ImportError: 
    getLangPrefsMethod = lambda req: map(
        lambda x: x.split(';')[0].strip(),
        req.get('HTTP_ACCEPT_LANGUAGE','').split(',')
        )

_marker = []

class I18NContentBase:

    def __init__(self, layer, REQUEST, verifypermission=1):
        self.layer=layer
        if not hasattr(REQUEST, 'set'): REQUEST=get_request()
        self.REQUEST=REQUEST
        available_languages=self.getFilteredLanguageMap(verifypermission=verifypermission).keys()
        self.languages=self.getLanguagesFromRequest() + list(available_languages)

    def Layer(self):
    	return self.layer

    def Languages(self):
    	return self.languages

    def getLanguagesFromRequest(self):

        language=self.REQUEST.cookies.get('I18N_CONTENT_LANGUAGE', None)
        language_once=self.REQUEST.get('cl', None)
        accept=self.getLanguagesFromTranslationService()
        try: default_language=self.Layer().portal_properties.site_properties.default_language
        except: default_language=None

        languages=accept
        if language: languages=[language,]+languages
        if language_once and language_once != language: languages=[language_once,]+languages
        if default_language: languages=languages+[default_language,]

	return languages

    def getLanguagesFromTranslationService(self):
        return getLangPrefsMethod(self.REQUEST)

    def getObject(self, verifypermission=1):
        # returns the object holding language information
        # for language self.language
        # ovewrite for each implementation
        raise NotImplementedError

    def getFilteredLanguageMap(self, verifypermission=1):
        # returns a language code to id mapping
        raise NotImplementedError

    def setServed(self, lang):
        self.REQUEST.set('I18N_CONTENT_SERVED_LANGUAGE', lang)
        self.served_language=lang

    def Served(self):
        try: return self.served_language
        except AttributeError: return None

    def existingLanguages(self, both=0):
        existing_languages=()
        existing_languages_long=()
        for code, name in self.Layer().availableLanguages():
            existing_languages=existing_languages+(code,)
            existing_languages_long=existing_languages_long+(name,)
        if not both: return existing_languages
        else: return existing_languages, existing_languages_long

class I18NContentLayer(I18NContentBase):

    def getFilteredLanguageMap(self, verifypermission=1):
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
                if _checkPermission(CMFCorePermissions.View, ob) or not verifypermission:
                    name = checker.name(id)
                    objs.update({id: name})
        return objs

    def getObject(self, verifypermission=1):

    	layer=self.Layer()
    	base = aq_base(layer)

        fallback=0
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
            raise Unauthorized, "you are not allowed to access this object"
        return None

class CheckValidity:

    def __init__(self, available_languages, available_languages_long):
        self.available_languages=available_languages
        self.available_languages_long=available_languages_long

    def check(self, lang):
        if self.available_languages:
            # check
            return lang in self.available_languages
        else:
            # failsave mode
            # check if len(lang) is 2 or 3
            if len(lang) == 2 or len(lang) == 3:
                return 1
            else: return 0

    def name(self, lang):
        if self.available_languages and self.available_languages_long:
            i=self.available_languages.index(lang)
            return self.available_languages_long[i]
        else: return 'Unknown'

schema = Schema((

    BaseSchema['id'],

    ObjectField(
        'allowedType',
        required=1,
        accessor="ContainmentContentType",
        mutator="setContainmentContentType",
        vocabulary="allowedContentTypeNames",
        widget=SelectionWidget
        ),

    ))

def modify_fti(fti):
    fti[0]['name']='I18NLayer'
    fti[0]['filter_content_types']=1
    # NOTE: we better hide the useless actions rather than delete them
    #       to keep compatibilty with templates requesting them
    for a in fti[0]['actions']:
        if a['id'] in ('references', 'metadata'): 
            a['visible'] = 0
    return fti

from Products.Archetypes.interfaces.base import IBaseObject
#from webdav.WriteLockInterface import WriteLockInterface

class I18NLayer( BaseFolder ):
    """ container object which transparently wraps multiple
        subobjects as language representations
    """
    schema = schema

    # XXX is that required ?
    isPrincipiaFolderish=0

    _containmentContentType=None
    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'view',
        'permissions': (CMFCorePermissions.View,),
        },{
        'id': 'languagelisting',
        'name'          : 'Language Listing',
        'action'        : 'i18nlayer_languages_form',
        'permissions'   : (CMFCorePermissions.AddPortalContent, CMFCorePermissions.ModifyPortalContent,),
		'visible'       : 1
        },{
        'id': 'defaultfallback',
        'name'          : 'Default Fallback Page',
        'action'        : 'i18nlayer_default_fallback',
        'permissions'   : (),
        'visible'       : 0
        })

    security = ClassSecurityInfo()
    # all stuff is public but not the protected
    security.declareObjectPublic()

    security.declarePrivate('retrieveContentLayer')
    def retrieveContentLayer(self, REQUEST=None, verifypermission=1):
        """ """
        # get request
        if not REQUEST: 
            try: REQUEST=self.REQUEST
            except: pass
        # make new contentlayer instance
        return I18NContentLayer(self, REQUEST, verifypermission=verifypermission)

    security.declarePrivate('retrieveLanguageContentUnprotected')
    def retrieveLanguageContentUnprotected(self):
        """ """
        return self.retrieveContentLayer(None,verifypermission=0).getObject(verifypermission=0)

    security.declarePublic('retrieveLanguageContent')
    def retrieveLanguageContent(self, REQUEST=None):
        """ """
        return self.retrieveContentLayer(REQUEST).getObject()

    security.declarePublic('retrieveI18NContentLayerOb')
    def retrieveI18NContentLayerOb(self, REQUEST=None):
        """ """
        return self

    security.declarePublic('retrieveI18NContentLayerURL')
    def retrieveI18NContentLayerURL(self, REQUEST=None):
        """ """
        return self.absolute_url()

    security.declarePublic('retrieveFilteredLanguages')
    def retrieveFilteredLanguages(self, REQUEST=None):
        """ """
        return self.retrieveContentLayer(REQUEST).getFilteredLanguageMap()

    security.declarePublic('retrieveExistingLanguages')
    def retrieveExistingLanguages(self, REQUEST=None):
        """ """
        return self.retrieveExistingLanguages()

    security.declarePublic('retrieveAcceptLanguages')
    def retrieveAcceptLanguages(self, REQUEST=None):
        """ """
        return self.retrieveContentLayer(REQUEST).getLanguagesFromTranslationService()

    def _checkId(self, id, allow_dup=0):
        ObjectManager._checkId(self, id, allow_dup)
        if not CheckValidity(None, None).check(id):
           raise 'Bad Request', ( 'The id "%s" is not allowed.' % id)
        # we are ok	

    security.declarePrivate('mapCore')
    def mapCore(self, name, *args, **kw):
        """maps methods on the given language object
        """

        try: ob = self.retrieveLanguageContent()
        except: ob=None
        if ob is not None:
            if hasattr(aq_base(ob), name):
                method = getattr(ob, name)
            elif getattr(aq_base(ob), 'isPrincipiaFolderish'):
                # allow non existing attributes for folderish objects
                return None
            else:
                raise "AttributeError", name
        else:
            method=I18NLayer.inheritedAttribute(name)
            args=(self,)+args
        if callable(method): return apply(method, args, kw)
        else: return method

    security.declarePublic('__call__')
    def __call__(self, *args, **kw):
        '''
        Invokes the default view
        '''
        # NOTE: returns view of an available object
        #       if non is available returns language sheet depended on permission
        #       of the current user on the layer

        ob = self.retrieveLanguageContent()
        if ob and ob != self: 
            view = _getViewFor(ob, 'view')
        else:
            ob=self
            alt='defaultfallback'
            if _checkPermission(ModifyPortalContent, ob): alt='languagelisting'
            view = _getViewFor(ob, alt)

        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
            return view()

    view = __call__

    def index_html(self, REQUEST, RESPONSE):
        '''return content if subobject has index_html method
        '''
        # NOTE: this implies for images and files which are returned directly when
        #       called with index_html.
        # NOTE: files download method is deprecated and not supported

        ob = self.retrieveLanguageContent()
        if ob:
            klass=ob.__class__
            i=getattr(klass,'index_html', None)
            c=getattr(klass,'__call__', None)
            if i and c and i != c:
                # XXX: probably we should set Content-Language somewhere here
                return apply(ob.index_html, (REQUEST, RESPONSE,), {})
        # no object so return view method
        return apply(self.__call__, (REQUEST, RESPONSE,), {})

    security.declarePublic('allowedContentTypeNames')
    def allowedContentTypeNames(self):
        '''
        returns a tuple with portal types current user can construct inside us 
        '''
        allowed=self.allowedContentTypes()

        portal_types=getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self)

        try: allowed.remove(myType)
        except: pass

        return map(lambda ti: ti.getId(), allowed)

    security.declarePublic('ContainmentContentType')
    def ContainmentContentType(self):
        '''returns the configured contenttype of this layer
        '''
        return self._containmentContentType or "Document"

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setContainmentContentType')
    def setContainmentContentType(self, content_type):
        '''sets the configured contenttype for this layer
        '''
        self._containmentContentType=content_type

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setI18NLayerAttributes')
    def setI18NLayerAttributes(self, id):
        '''stores required attributes to a given object (has to be subobject of myself)
        '''
        if not hasattr(aq_base(self),id): raise "AttributeError", id
        ob=getattr(self,id)
        if not _checkPermission(ModifyPortalContent, ob):
            raise "Unauthorized"

        # the language is the same as the id
        lang=id
        setattr(ob, 'i18nContent_language', lang)

    security.declarePublic('title_or_id')
    def title_or_id(self):
        """ """
        title=self.mapCore('title')
        if title: return title
        return self.getId()

    security.declarePublic('get_size')
    def get_size(self):
        """WebDAV needs this
        """
        try: return self.mapCore('get_size')
        except: return None

    getSize=get_size

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """ """
        return self.mapCore('getIcon', relative_to_portal=relative_to_portal)

    security.declarePublic('Title')
    def Title(self):
        """ """
        return self.mapCore('Title')

    security.declarePublic('Creator')
    def Creator(self):
        """ """
        return self.mapCore('Creator')

    security.declarePublic('Subject')
    def Subject(self):
        """ """
        return self.mapCore('Subject')

    security.declarePublic('Publisher')
    def Publisher(self):
        """ """
        return self.mapCore('Publisher')

    security.declarePublic('Description')
    def Description(self):
        """ """
        return self.mapCore('Description')

    security.declarePublic('Contributors')
    def Contributors(self):
        """ """
        return self.mapCore('Contributors')

    security.declarePublic('Date')
    def Date(self):
        """ """
        return self.mapCore('Date')

    security.declarePublic('CreationDate')
    def CreationDate(self):
        """ """
        return self.mapCore('CreationDate')

    security.declarePublic('EffectiveDate')
    def EffectiveDate(self):
        """ """
        return self.mapCore('EffectiveDate')

    security.declarePublic('ExpirationDate')
    def ExpirationDate(self):
        """ """
        return self.mapCore('ExpirationDate')

    security.declarePublic('ModificationDate')
    def ModificationDate(self):
        """ """
        return self.mapCore('ModificationDate')

    security.declarePublic('Type')
    def Type(self):
        """ """
        return self.mapCore('Type')

    security.declarePublic('Format')
    def Format(self):
        """ """
        return self.mapCore('Format')

    security.declarePublic('Identifier')
    def Identifier(self):
        """ """
        return self.mapCore('Identifier')

    security.declarePublic('Language')
    def Language(self):
        """ """
        return self.retrieveContentLayer().Served()

    security.declarePublic('Rights')
    def Rights(self):
        """ """
        return self.mapCore('Rights')

    def content_type(self):
        """WebDAV needs this
        """
        try: return self.Format()
        except: return 'application/unknown'

    security.declarePublic('isEffective')
    def isEffective(self, date):
        """ """
        return self.mapCore('isEffective', date)

    security.declarePublic('created')
    def created(self):
        """ """
        return self.mapCore('created')

    security.declarePublic('effective')
    def effective(self):
        """ """
        return self.mapCore('effective')

    security.declarePublic('expires')
    def expires(self):
        """ """
        return self.mapCore('expires')

    security.declarePublic('modified')
    def modified(self):
        """ """
        return self.mapCore('modified')

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """Index the object in the portal catalog.
        """
        pass

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """Unindex the object from the portal catalog.
        """
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """
            Reindex the object in the portal catalog.
            If idxs is present, only those indexes are reindexed.
            The metadata is always updated.

            Also update the modification date of the object,
            unless specific indexes were requested.
        """
        pass

registerType(I18NLayer)


