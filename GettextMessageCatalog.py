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
"""A simple implementation of a Message Catalog. 

$Id: GettextMessageCatalog.py,v 1.1 2003/01/02 15:29:12 lalo Exp $
"""

from gettext import GNUTranslations
import os
import codecs
from types import DictType, StringType, UnicodeType

# template to use to write missing entries to .missing
missing_template = u"""msgid "%(id)s"
msgstr ""
"""

orig_text_template = u"""
#. %(text)s
"""

orig_text_line_joiner = u"\n#. "

class GettextMessageCatalog:
    """ """

    def __init__(self, path_to_file):
        """Initialize the message catalog"""
        self._path_to_file = path_to_file
        self.__translation_object = None
        self._prepareTranslations()
    

    def _prepareTranslations(self):
        """ """
        if self.__translation_object is None:
            file = open(self._path_to_file, 'r')
            tro = GNUTranslations(file)
            file.close()
            self._language = (tro._info.get('language-code', None) # new way
                           or tro._info.get('language', None)) # old way
            self._domain = tro._info.get('domain', None)
            if self._language is None or self._domain is None:
                raise ValueError, 'potfile has no metadata'
            self.__translation_object = tro
            missing = self._path_to_file[:-1] + 'issing'
            if os.access(missing, os.W_OK):
                self.__missing = codecs.open(missing, 'a',
                                             self.__translation_object._charset)
            else:
                self.__missing = None
            

    def getMessage(self, id, orig_text=None):
        """
        """
        self._prepareTranslations()
        msg = self.__translation_object.gettext(id)
        if msg is id:
            if self.__missing:
                if orig_text:
                    orig_text = orig_text_line_joiner.join(orig_text.split('\n'))
                    self.__missing.write(orig_text_template % {'text': orig_text})
                self.__missing.write(missing_template % {'id':id.replace('"', r'\"')})
                self.__missing.flush()
            raise KeyError
        if type(msg) is StringType:
            msg = unicode(msg, self.__translation_object._charset)
        return msg

    def queryMessage(self, id, default=None):
        """
        """
        try:
            return self.getMessage(id, default)
        except KeyError:
            if default is None:
                default = id
            return default

    def getLanguage(self):
        """
        """
        return self._language
        
    def getDomain(self):
        """
        """
        return self._domain

    def getIdentifier(self):
        """
        """
        return self._path_to_file

    def getInfo(self, name):
        """
        """
        return self.__translation_object._info.get(name, None)
        
    #
    ############################################################
