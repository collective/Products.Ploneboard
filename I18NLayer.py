# Copyright (C) 2003-2004 strukturAG <simon@struktur.de>
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

$Id: I18NLayer.py,v 1.16 2004/03/02 13:12:57 longsleep Exp $
"""

__version__ = "$Revision: 1.16 $"

from Globals import get_request
from Acquisition import aq_acquire, aq_base, aq_inner, aq_chain, aq_parent, ImplicitAcquisitionWrapper
from OFS.ObjectManager import ObjectManager
from Products.CMFCore.utils import _verifyActionPermissions, _checkPermission
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents, ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG
from Products.Archetypes.public import *
try: from Products.Archetypes.BaseFolder import BaseFolderMixin # AT1.2.x
except ImportError: from Products.Archetypes.BaseFolder import BaseFolder as BaseFolderMixin # AT1.0.x
from Products.CMFPlone.PloneFolder import _getViewFor

from I18NContent import I18NContentLayer
from utils import CheckValidity


schema = Schema((

    BaseSchema['id'],

    ObjectField(
        'allowedType',
        required=1,
        default=None,
        accessor="ContainmentContentType",
        mutator="setContainmentContentType",
        vocabulary="allowedContentTypeNames",
        widget=SelectionWidget(   description = "Select the type of documents which this I18NLayer shall contain.",
                                  description_msgid = "help_containmenttype",
                                  label = "contains Type",
                                  i18n_domain = 'i18nlayer',
                                  label_msgid = "label_containmenttype" )
        ),
    ))


class TitleLessBaseFolder( BaseFolderMixin, DefaultDublinCoreImpl ):
    """ we need a basefolder without title and 
        without extended meta data and the other crap
        NOTE: this is for at1.2.x .. hopefully implementation will be cleaner in at1.3 and newer
    """

    def Title(self, **kwargs):
        """ we dont have a title """
        return ''

    def setTitle(self, value, **kwargs):
        """ we dont have a title """
        pass


class I18NLayer( TitleLessBaseFolder ):
    """ container object which transparently wraps multiple
        subobjects as language representations
    """
    schema = schema
    isPrincipiaFolderish=0

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'view',
        'permissions': (CMFCorePermissions.View,),
        },{
        'id': 'languagelisting',
        'name'          : 'Translate',
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

    # all stuff is public
    security.declareObjectPublic()

    
    security.declarePrivate('retrieveContentLayer')
    def retrieveContentLayer(self, REQUEST=None, verifypermission=1):
        """ returns the contentlayer helper instance """
        # get request
        if not REQUEST:
            REQUEST = get_request()
        # make new contentlayer instance
        return I18NContentLayer(self, REQUEST, verifypermission=verifypermission)


    security.declarePrivate('retrieveLanguageContentUnprotected')
    def retrieveLanguageContentUnprotected(self):
        """ provides a method to get the requested language object
            without permission checks """
        return self.retrieveContentLayer(None,verifypermission=0).getObject(verifypermission=0)


    security.declarePublic('retrieveLanguageContent')
    def retrieveLanguageContent(self, REQUEST=None):
        """ public method to get the requested language object
            including permission checks """
        return self.retrieveContentLayer(REQUEST).getObject()


    security.declarePublic('retrieveI18NContentLayerOb')
    def retrieveI18NContentLayerOb(self, REQUEST=None):
        """ helper to get the i18nlayer object easily """
        return self


    security.declarePublic('retrieveI18NContentLayerURL')
    def retrieveI18NContentLayerURL(self, REQUEST=None):
        """ get the i18nlayers url easily """
        return self.absolute_url()


    security.declarePublic('retrieveFilteredLanguages')
    def retrieveFilteredLanguages(self, REQUEST=None):
        """ returns a mapping of the filtered languages """
        return self.retrieveContentLayer(REQUEST).getFilteredLanguageMap()


    security.declarePublic('retrieveExistingLanguages')
    def retrieveExistingLanguages(self, REQUEST=None, both=0):
        """ returns a list of existing languages """
        return self.retrieveContentLayer(REQUEST).existingLanguages(both=both)

    
    security.declarePublic('retrieveAcceptLanguages')
    def retrieveAcceptLanguages(self, REQUEST=None):
        """ returns a list of acceptable languages """
        return self.retrieveContentLayer(REQUEST).getLanguagesFromTranslationService()


    def _checkId(self, id, allow_dup=0):
        # we only allow valid languages as id
        ObjectManager._checkId(self, id, allow_dup)
        if id.startswith('.'):
            # allow ids starting with . to make inline copy/paste/rename possible
            return 
        # check with the language validity checker
        # try to retrieve valid language codes from plonelanguage tool
        allowed_languages, allowed_languages_long = self.retrieveExistingLanguages(both=1)
        if not CheckValidity(allowed_languages, allowed_languages_long).check(id):
            raise 'Bad Request', ( 'The id "%s" is not allowed.' % id)
        # we are ok


    security.declarePrivate('mapCore')
    def mapCore(self, name, default=None, *args, **kw):
        """
        maps methods on the given language object
        """

        try: ob = self.retrieveLanguageContent()
        except: ob=None
        if ob is not None:

            if hasattr(aq_base(ob), name):
                method = getattr(ob, name)
            elif getattr(aq_base(ob), 'isPrincipiaFolderish') or isinstance(ob, I18NLayer):
                # allow non existing attributes for folderish objects
                return default
            else:
                raise "AttributeError", name
        else:
            method=I18NLayer.inheritedAttribute(name)
            args=(self,)+args

        if callable(method): return apply(method, args, kw)
        else: return method


    security.declarePublic('__call__')
    def __call__(self, *args, **kw):
        """
        Invokes the default view
        """
        # NOTE: returns view of an available object
        #       if none is available returns language sheet depended on permission
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

    security.declarePublic('view')
    def view(self, REQUEST, RESPONSE, **kw):
        """
        redirect to subobject when forcing language urls
        """
        ob = self.retrieveLanguageContent()
        language_tool = getToolByName(self, 'portal_languages', None)
        force_redir = getattr(language_tool, 'force_language_urls', 1)       
        if force_redir and ob:
            view = _getViewFor(ob, 'view')
            url = "%s/%s" % (ob.absolute_url(), view.getId())
            if REQUEST.get('QUERY_STRING', '').strip(): url="%s?%s" % (url, REQUEST.QUERY_STRING)
            REQUEST.RESPONSE.redirect(url)
            return "redirect view"
        return apply(self.__call__, (REQUEST, RESPONSE,), kw)
    

    security.declarePublic('index_html')    
    def index_html(self, REQUEST, RESPONSE):
        """
        return content if subobject has index_html method
        or redirect to subobjects index_html when forcing language urls
        """
        # NOTE: this implies for images and files which are returned directly when
        #       called with index_html.
        # NOTE: files download method is deprecated and not supported

        ob = self.retrieveLanguageContent()
        if ob:
            klass=ob.__class__
            language_tool = getToolByName(self, 'portal_languages', None)
            force_redir = getattr(language_tool, 'force_language_urls', 1)  
            if force_redir:
                url = "%s" % (ob.absolute_url())
                if REQUEST.get('QUERY_STRING', '').strip(): url="%s?%s" % (url, REQUEST.QUERY_STRING)
                REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
                REQUEST.RESPONSE.setHeader('Expires', '-1')
                REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')                                        
                REQUEST.RESPONSE.redirect(url)
                return "redirect index"
            i=getattr(klass,'index_html', None)
            c=getattr(klass,'__call__', None)
            if i and c and i != c:
                # XXX: probably we should set Content-Language somewhere here
                return apply(ob.index_html, (REQUEST, RESPONSE,), {})

        # no object so call us
        return apply(self.__call__, (REQUEST, RESPONSE,), {})

 
    security.declarePublic('allowedContentTypeNames')
    def allowedContentTypeNames(self):
        """
        returns a tuple with portal types current user can construct inside us
        """
        allowed=self.allowedContentTypes()

        portal_types=getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self)

        try: allowed.remove(myType)
        except: pass

        return map(lambda ti: ti.getId(), allowed)


    security.declarePublic('ContainmentContentType')
    def ContainmentContentType(self):
        '''
        returns the configured contenttype of this layer
        '''
        return self._containmentContentType or "Document"


    security.declarePublic('ContainmentMetaType')
    def ContainmentMetaType(self):
        '''
        returns the configures metatype of this layer
        '''
        try:
            typestool = getToolByName(self, 'portal_types')
            ti=typestool.getTypeInfo(self.ContainmentContentType())
            return ti.Metatype()
        except:
            return self.meta_type


    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setContainmentContentType')
    def setContainmentContentType(self, content_type):
        '''
        sets the configured contenttype for this layer
        '''
        self._containmentContentType=content_type


    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setI18NLayerAttributes')
    def setI18NLayerAttributes(self, id, ob=None):
        '''
        stores required attributes to a given object
        either to a subobject of myself or to ob
        '''
        if not ob:
            if not hasattr(aq_base(self),id): raise "AttributeError", id
            ob=getattr(self,id)

        if not _checkPermission(ModifyPortalContent, ob):
            raise "Unauthorized"

        # the language is the same as the id
        lang=id
        setattr(ob,'i18nContent_language', lang)


    security.declarePublic('listFolderContents')
    def listFolderContents(self, spec=None, contentFilter=None):
        """ map containers helper method
            we return the language objects contents if its folderish 
        """
        try: return self.mapCore('listFolderContents', default=(), spec=spec, contentFilter=contentFilter)
        except: return I18NLayer.inheritedAttribute('listFolderContents')(self, spec=spec, contentFilter=contentFilter)


    security.declarePublic('contentValues')
    def contentValues(self, spec=None, filter=None):
        """ map containers helper method 
            we return the language objects contents if its folderish
        """
        try: return self.mapCore('contentValues', default=(), spec=spec, filter=filter)
        except: return I18NLayer.inheritedAttribute('contentValues')(self, spec=spec, filter=filter)


    security.declarePublic('title_or_id')
    def title_or_id(self):
        """ return the language objects title_or_id """
        title=self.mapCore('title')
        if title: return title
        return self.getId()

    security.declarePublic('get_size')
    def get_size(self):
        """
        WebDAV needs this
        we return the language objects size
        """
        try: return self.mapCore('get_size')
        except: return None

    getSize=get_size

    security.declarePublic('tag')
    def tag(self, *args, **kw):
        """ map the tag method """
        return self.mapCore('tag', *args, **kw)

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """ we display the language objects icon """
        return self.mapCore('getIcon', relative_to_portal=relative_to_portal)

    security.declarePublic('CookedBody')
    def CookedBody(self, stx_level=None, setlevel=0):
        """ needed to support standard renderable types """
        return self.mapCore('CookedBody', stx_level=stx_level, setlevel=setlevel)

    security.declarePublic('Title')
    def Title(self):
        """ dublincore meta data support """
        return self.mapCore('Title')

    security.declarePublic('Creator')
    def Creator(self):
        """ dublincore meta data support """
        return self.mapCore('Creator')

    security.declarePublic('Subject')
    def Subject(self):
        """ dublincore meta data support """
        return self.mapCore('Subject', default=())

    security.declarePublic('Publisher')
    def Publisher(self):
        """ dublincore meta data support """
        return self.mapCore('Publisher')

    security.declarePublic('Description')
    def Description(self):
        """ dublincore meta data support """
        return self.mapCore('Description')

    security.declarePublic('Contributors')
    def Contributors(self):
        """ dublincore meta data support """
        return self.mapCore('Contributors')

    security.declarePublic('Date')
    def Date(self):
        """ dublincore meta data support """
        return self.mapCore('Date')

    security.declarePublic('CreationDate')
    def CreationDate(self):
        """ dublincore meta data support """
        return self.mapCore('CreationDate')

    security.declarePublic('EffectiveDate')
    def EffectiveDate(self):
        """ dublincore meta data support """
        return self.mapCore('EffectiveDate')

    security.declarePublic('ExpirationDate')
    def ExpirationDate(self):
        """ dublincore meta data support """
        return self.mapCore('ExpirationDate')

    security.declarePublic('ModificationDate')
    def ModificationDate(self):
        """ dublincore meta data support """
        return self.mapCore('ModificationDate')

    security.declarePublic('Type')
    def Type(self):
        """ dublincore meta data support """
        return self.mapCore('Type')

    security.declarePublic('Format')
    def Format(self):
        """ dublincore meta data support """
        return self.mapCore('Format')

    security.declarePublic('Identifier')
    def Identifier(self):
        """ dublincore meta data support """
        return self.mapCore('Identifier')

    security.declarePublic('Language')
    def Language(self):
        """ dublincore meta data support """
        return self.retrieveContentLayer().Served()

    security.declarePublic('Rights')
    def Rights(self):
        """ dublincore meta data support """
        return self.mapCore('Rights')

    def content_type(self):
        """
        WebDAV needs this
        """
        try: return self.Format()
        except: return 'application/unknown'

    security.declarePublic('isEffective')
    def isEffective(self, date):
        """ publication meta data """
        return self.mapCore('isEffective', date)

    security.declarePublic('created')
    def created(self):
        """ dublincore meta data support """
        return self.mapCore('created')

    security.declarePublic('effective')
    def effective(self):
        """ publication meta data """
        return self.mapCore('effective')

    security.declarePublic('expires')
    def expires(self):
        """ publication meta data """
        return self.mapCore('expires')

    security.declarePublic('modified')
    def modified(self):
        """ meta data support """
        return self.mapCore('modified')

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """ we dont index i18nlayer into catalog """
        pass

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """ as are not indexed we dont have to unindex """
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """ no indexing of i18nlayers """
        pass


def modify_fti(fti):
    fti['name']='I18NLayer'
    fti['filter_content_types']=1
    fti['content_icon']='i18nlayer_icon.gif'
    # NOTE: we better hide the useless actions rather than delete them
    #       to keep compatibilty with templates requesting them
    for a in fti['actions']:
        if a['id'] in ('references', 'metadata'):
            a['visible'] = 0
    return fti


registerType(I18NLayer)


