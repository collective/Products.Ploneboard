##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, LUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Message IDs.

Message Id factor based on the i18n/messageid file of Zope 3.

Adapted for the Placeless Translation Service by Christian Heimes

$Id: MessageID.py,v 1.2 2004/02/03 22:14:42 tiran Exp $
"""

from Globals import InitializeClass, get_request
from AccessControl import ClassSecurityInfo
from Products.PlacelessTranslationService import translate, utranslate
from types import BuiltinFunctionType, UnicodeType, StringType


class MessageIDBase:
    """Message ID.

    This is a string used as a message ID.  It has a domain attribute that is
    its source domain, and a default attribute that is its default text to
    display when there is no translation.  domain may be None meaning there is
    no translation domain.  default may also be None, in which case the
    message id itself implicitly serves as the default text.

    MessageID objects also have a mapping attribute which must be set after
    construction of the object.  This is used when translating and
    substituting variables.
    """
    security = ClassSecurityInfo()

    def __init__(self, ustr, domain=None, default=None, default_encoding=None):
        self.ustr = ustr
        self.domain  = domain
        if default is None:
            self.default = self.ustr
        else:
            self.default = default
        self.default_encoding = default_encoding
        self.mapping = {}

    def translate(self):
        pass

    def __str__(self):
        pass

    def __call__(self):
        return self.translate()
    
    def __getattr__XXX(self, func):
        """try to emulate class MessageID(unicode)
        """
        attr = getattr(self(), func, None)
        if attr and type(attr) is BuiltinFunctionType:
            return attr
        raise AttributeError("'MessageId' has no attribute '%s'" % func)

InitializeClass(MessageIDBase)


class MessageID(MessageIDBase):
    """non unicode MessageID
    """
    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self):
        """translate the message id
        """
        return translate(domain=self.domain, 
                            msgid=self.ustr, 
                            context=get_request(),
                            mapping=self.mapping,
                            default=self.default)

    def __str__(self):
        return str(self.translate())

InitializeClass(MessageID)


class MessageIDUnicode(MessageIDBase):
    """unicode MessageID
    """
    security = ClassSecurityInfo()
    
    def __init__(self, ustr, domain=None, default=None, default_encoding=None):
        MessageIDBase.__init__(self, ustr, domain, default, default_encoding)
        if default_encoding and type(ustr) is not UnicodeType:
            ustr = unicode(ustr, default_encoding)
        else:
            ustr = unicode(ustr)
        self.ustr = ustr
        if default is None:
            self.default = ustr
        else:    
            if default_encoding and type(ustr) is not UnicodeType:
                self.default = unicode(default, default_encoding)
            else:
                self.ustr = unicode(default)

    security.declarePublic('translate')
    def translate(self):
        """translate the message id
        """

        return utranslate(domain=self.domain, 
                            msgid=self.ustr, 
                            context=get_request(),
                            mapping=self.mapping,
                            default=self.default)

    def __str__(self):
        return unicode(self.translate())

InitializeClass(MessageIDUnicode)


class MessageIDFactory:
    """Factory for creating MessageIDs
    """
    security = ClassSecurityInfo()

    def __init__(self, domain, as_unicode=False, default_encoding=None):
        self._domain = domain
        self._as_unicode = as_unicode
        self._default_encoding = default_encoding

    def __call__(self, ustr, default=None):
        """used for _()

        ustr - the message id
        default - the default string if the message id isn't the default
        """
        if self._as_unicode:
            return MessageIDUnicode(ustr, domain=self._domain,
                                    default=default, 
                                    default_encoding=self._default_encoding)
        else:
            return MessageID(ustr, domain=self._domain,
                             default=default,
                             default_encoding=self._default_encoding)

InitializeClass(MessageIDFactory)
