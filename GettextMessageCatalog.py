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
"""A simple implementation of a Message Catalog.

$Id: GettextMessageCatalog.py,v 1.8 2004/02/03 22:14:42 tiran Exp $
"""

from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from Globals import InitializeClass
from gettext import GNUTranslations
import os, sys, types, codecs, traceback, zLOG
from OFS.Traversable import Traversable
from Persistence import Persistent, Overridable
from Acquisition import Implicit
from App.Management import Tabs
import re
from OFS.Uninstalled import BrokenClass
from utils import log, Registry
from msgfmt import Msgfmt
from DateTime import DateTime
import Globals

try:
    True
except NameError:
    True=1
    False=0

try:
    from Products.OpenPT.OpenPTFile import OpenPTFile as ptFile
except ImportError:
    from Products.PageTemplates.PageTemplateFile import PageTemplateFile
    from Globals import package_home
    def ptFile(id, *filename):
        if type(filename[0]) is types.DictType:
            filename = list(filename)
            filename[0] = package_home(filename[0])
        filename = os.path.join(*filename)
        if not os.path.splitext(filename)[1]:
            filename = filename + '.pt'
        return PageTemplateFile(filename, '', __name__=id)

# template to use to write missing entries to .missing
missing_template = u"""msgid "%(id)s"
msgstr ""
"""

orig_text_template = u"""
#. %(text)s
"""

orig_text_line_joiner = u"\n#. "

permission = 'View management screens'

translationRegistry = Registry()
registerTranslation = translationRegistry.register

def getMessage(catalog, id, orig_text=None):
    """get message from catalog
    
    returns the message according to the id 'id' from the catalog 'catalog' or
    raises a KeyError if no translation was found. The return type is always
    unicode
    """
    msg = catalog.gettext(id)
    if msg is id:
        raise KeyError
    if type(msg) is types.StringType:
        msg = unicode(msg, catalog._charset)
    return msg


class BrokenMessageCatalog(Persistent, Implicit, Traversable, Tabs):
    """ broken message catalog """
    meta_type = title = 'Broken Gettext Message Catalog'
    icon='p_/broken'
    __roles__=('Manager',)
    title__roles__=__roles__

    security = ClassSecurityInfo()
 
    def __init__(self, pofile, error):
        self._pofile = pofile
        self.id = os.path.split(self._pofile)[-1]
        self._mod_time = self._getModTime()
        self.error = traceback.format_exception(error[0],error[1],error[2])

    # modified time helper
    def _getModTime(self):
        """
        """
        try:
            mtime = os.stat(self._pofile)[8]
        except IOError:
            mtime = 0
        return mtime

    def getIdentifier(self):
        """
        """
        return self.id

    def getId(self):
        """
        """
        return self.id

    getError__roles__ = __roles__
    def getError(self):
        """
        """
        return self.error

    Title__roles__ = __roles__
    def Title(self):
        return self.title


    def get_size(self):
        """Get the size of the underlying file."""
        return os.path.getsize(self._pofile)


    def reload(self, REQUEST=None):
        """ Forcibly re-read the file """
        # get pts
        pts = aq_parent(self)
        name = self.getId()
        pofile = self._pofile
        pts._delObject(name)
        try: pts.addCatalog(GettextMessageCatalog(pofile))
        except:
            exc=sys.exc_info()
            log('Message Catalog has errors', zLOG.PROBLEM, name, exc)
            pts.addCatalog(BrokenMessageCatalog(pofile, exc))
        self = pts._getOb(name)
        if hasattr(REQUEST, 'RESPONSE'):
            if not REQUEST.form.has_key('noredir'):
                REQUEST.RESPONSE.redirect(self.absolute_url())
        

    file_exists__roles__ = __roles__
    def file_exists(self):
        try:             
            file = open(self._pofile, 'rb')
        except:
            return False
        return True


    def manage_afterAdd(self, item, container): pass
    def manage_beforeDelete(self, item, container): pass
    def manage_afterClone(self, item): pass
                                                            
    manage_options = (
        {'label':'Info', 'action':''},
        )
                                                            
    index_html = ptFile('index_html', globals(), 'www', 'catalog_broken')

#XXX InitializeClass(BrokenMessageCatalog)


class GettextMessageCatalog(Persistent, Implicit, Traversable, Tabs):
    """
    Message catalog that wraps a .po file in the filesystem and stores
    the compiled po file in the zodb
    """
    meta_type = title = 'Gettext Message Catalog'
    icon = 'misc_/PlacelessTranslationService/GettextMessageCatalog.png'
    __roles__=('Manager',)
    title__roles__=__roles__

    security = ClassSecurityInfo()
    
    def __init__(self, pofile):
        """Initialize the message catalog"""
        self._pofile = pofile
        self.id = os.path.split(self._pofile)[-1]
        self._mod_time = self._getModTime()
        self._prepareTranslations(0)

    def _prepareTranslations(self, catch=1):
        """Try to generate the translation object
           if fails remove us from registry
        """
        try: self._doPrepareTranslations()
        except:
            if self.getId() in translationRegistry.keys():
                del translationRegistry[self.getId()]
            if not catch: raise
            else: pass 

    def _doPrepareTranslations(self):
        """Generate the translation object from a po file
        """
        self._updateFromFS()
        tro = None
        if getattr(self, '_v_tro', None) is None:
            self._v_tro = tro = translationRegistry.get(self.getId(), None)
        if tro is None:
            moFile = self._getMoFile()
            tro = GNUTranslations(moFile)
            self._language = (tro._info.get('language-code', None) # new way
                           or tro._info.get('language', None)) # old way
            self._domain = tro._info.get('domain', None)
            if self._language is None or self._domain is None:
                raise ValueError, 'potfile has no metadata, PTS needs a language and a message domain!'
            self._language = self._language.lower().replace('_', '-')
            self._other_languages = tro._info.get('x-is-fallback-for', '').split()
            self.preferred_encodings = tro._info.get('preferred-encodings', '').split()
            self.name = unicode(tro._info.get('language-name', ''), tro._charset)
            self.default_zope_data_encoding = tro._charset
            translationRegistry[self.getId()] = self._v_tro = tro
            missingFileName = self._pofile[:-2] + '.missing'
            if os.access(missingFileName, os.W_OK):
                self._missing = MissingIds(missingFileName, self._v_tro._charset)
            else:
                self._missing = None
            if self.name:
                self.title = '%s language (%s) for %s' % (self._language, self.name, self._domain)
            else:
                self.title = '%s language for %s' % (self._language, self._domain)

    def filtered_manage_options(self, REQUEST=None):
        return self.manage_options

    def reload(self, REQUEST=None):
        """Forcibly re-read the file
        """
        if self.getId() in translationRegistry.keys():
            del translationRegistry[self.getId()]
        if hasattr(self, '_v_tro'):
            del self._v_tro
        name = self.getId()
        pts = aq_parent(self)
        pofile=self._pofile
        try:
            self._prepareTranslations(0)
            log('reloading %s: %s' % (self.getId(), self.title), severity=zLOG.BLATHER)
        except:
            pts._delObject(name)
            exc=sys.exc_info()
            log('Message Catalog has errors', zLOG.PROBLEM, name, exc)
            pts.addCatalog(BrokenMessageCatalog(pofile, exc))
        self = pts._getOb(name)
        if hasattr(REQUEST, 'RESPONSE'):
            if not REQUEST.form.has_key('noredir'):
                REQUEST.RESPONSE.redirect(self.absolute_url())

    def _log_missing(self, id, orig_text):
        """Logging missing ids
        """
        if self._missing is None:
            return
        self._missing.log(id, orig_text)

    def getMessage(self, id, orig_text=None, testing=False):
        """get message from catalog
        """
        self._prepareTranslations()
        try:
            msg = getMessage(self._v_tro, id, orig_text)
        except KeyError:
            if not testing:
                self._log_missing(id, orig_text)
            raise
        return msg

    queryMessage__roles__ = None # Public
    def queryMessage(self, id, default=None):
        """Queries the catalog for a message
        
        If the message wasn't found the default value or the id is returned.
        """
        try:
            return self.getMessage(id, default) #, testing=True)
        except KeyError:
            if default is None:
                default = id
            return default

    def getLanguage(self):
        """
        """
        return self._language

    def getLanguageName(self):
        """
        """
        return self.name or self._language

    def getOtherLanguages(self):
        """
        """
        return self._other_languages

    def getDomain(self):
        """
        """
        return self._domain

    def getIdentifier(self):
        """
        """
        return self.id

    def getId(self):
        """
        """
        return self.id

    def getInfo(self, name):
        """
        """
        self._prepareTranslations()
        return self._v_tro._info.get(name, None)

    Title__roles__ = __roles__
    def Title(self):
        return self.title
        
    def _getMoFile(self):
        """get compiled version of the po file as file object
        """
        mo = Msgfmt(self._readFile())
        return mo.getAsFile()
        
    def _readFile(self, reparse=False):
        """Read the data from the filesystem.
        
        """ 
        file = open(self._pofile, 'rb')
        data = []
        try:
             # XXX need more checks here
             data = file.readlines()
        finally:
             file.close()
        return data 
        
    def _updateFromFS(self):
        """Refresh our contents from the filesystem
        
        if the file is newer and we are running in debug mode.
        """
        if Globals.DevelopmentMode:
            mtime = self._getModTime()
            if mtime != self._mod_time:
                self._mod_time = mtime
                self.reload()

    def _getModTime(self):
        """
        """
        try:
            mtime = os.stat(self._pofile)[8]
        except IOError:
            mtime = 0
        return mtime

    def get_size(self):
        """Get the size of the underlying file."""
        return os.path.getsize(self._pofile)

    def getModTime(self):
        """Return the last_modified date of the file we represent.

        Returns a DateTime instance.
        """
        self._updateFromFS()
        return DateTime(self._mod_time)

    def getObjectFSPath(self):
        """Return the path of the file we represent"""
        return self._pofile

    ############################################################
    # Zope/OFS integration

    def manage_afterAdd(self, item, container): pass
    def manage_beforeDelete(self, item, container): pass
    def manage_afterClone(self, item): pass

    manage_options = (
        {'label':'Info', 'action':''},
        {'label':'Test', 'action':'zmi_test'},
        )

    index_html = ptFile('index_html', globals(), 'www', 'catalog_info')

    zmi_test = ptFile('zmi_test', globals(), 'www', 'catalog_test')

    file_exists__roles__ = __roles__
    def file_exists(self):
        try:
            file = open(self._pofile, 'rb')
        except:
            return False
        return True

    getEncoding__roles__ = __roles__
    def getEncoding(self):
        try:
            content_type = self.getHeader('content-type')
            enc = content_type.split(';')[1].strip()
            enc = enc.split('=')[1]
        except: enc='utf-8'
        return enc

    getHeader__roles__ = __roles__
    def getHeader(self, header):
        self._prepareTranslations()
        info = self._v_tro._info
        return info.get(header)

    displayInfo__roles__ = __roles__
    def displayInfo(self):
        self._prepareTranslations()
        try: info = self._v_tro._info
        except: 
            # broken catalog probably
            info={}
        keys = info.keys()
        keys.sort()
        return [{'name': k, 'value': info[k]} for k in keys] + [
            {'name': 'full path', 'value': self._pofile},
            {'name': 'last modification', 'value': self.getModTime().ISO()}
            ]
    #
    ############################################################

#XXX InitializeClass(GettextMessageCatalog)

class MissingIds(Persistent):
    
    security = ClassSecurityInfo()

    def __init__(self, fileName, charset):
        self._fileName = fileName
        self._charset = charset
        self._ids = {}
        self._pattern = re.compile('msgid "(.*)"$')
        self.parseFile()
        self._v_file = None

    def parseFile(self):
        file = codecs.open(self._fileName, 'r', self._charset)
        for line in file.xreadlines():
            match = self._pattern.search(line)
            if match:
                msgid = match.group(1)
                self._ids[msgid] = 1
        file.close()

    def log(self, msgid, orig_text):
        if not self._ids.has_key(msgid):
            if getattr(self, '_v_file', None) is None:
              self._v_file = codecs.open(self._fileName, 'a', self._charset)
            if orig_text:
                orig_text = orig_text_line_joiner.join(orig_text.split('\n'))
                self._v_file.write(orig_text_template % {'text': orig_text})
            self._v_file.write(missing_template % {'id':msgid.replace('"', r'\"')})
            self._v_file.flush()
            self._ids[msgid]=1

#XXX InitializeClass(MissigIds)
