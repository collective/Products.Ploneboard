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

$Id: MessageID.py,v 1.1 2004/01/28 13:41:59 tiran Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService
from types import BuiltinFunctionType, UnicodeType

class MessageID:
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

    def __init__(self, ustr, domain=None, default=None, context=None, default_encoding=None):
        if default_encoding and type(ustr) is not UnicodeType:
            self.ustr = unicode(ustr, default_encoding)
        else:
            self.ustr = unicode(ustr)
        if not context and not hasattr(context, 'REQUEST'):
            raise ValueError("'MessageId' needs a valid context")
        self.context = context
        self.domain  = domain
        if default is None:
            self.default = ustr
        else:
            if default_encoding and type(ustr) is not UnicodeType:
                self.default = unicode(default, default_encoding)
            else:
                self.ustr = unicode(default)
        self.default_encoding = default_encoding
        self.mapping = {}

    security.declarePublic('translate')
    def translate(self):
        """translate the message id
        """
        service = getGlobalTranslationService()
        return service.translate(domain=self.domain, 
                            msgid=self.ustr, 
                            context=self.context,
                            mapping=self.mapping,
                            default=self.default)

    __str__ = __call__ = translate
    
    def __getattr__XXX(self, func):
        """try to emulate class MessageID(unicode)
        """
        attr = getattr(self(), func, None)
        if attr and type(attr) is BuiltinFunctionType:
            return attr
        raise AttributeError("'MessageId' has no attribute '%s'" % func)

    def __getstate__(self):
        return self.context, self.ustr, self.domain, self.default, self.mapping

    def __setstate__(self, (context, ustr, domain, default, mapping)):
        self.context = context
        self.ustr    = ustr
        self.domain  = domain
        if default is None:
            self.default = ustr
        else:
            self.default = default
        self.mapping = mapping

InitializeClass(MessageID)

class MessageIDFactory:
    """Factory for creating MessageIDs."""
    security = ClassSecurityInfo()

    def __init__(self, domain, default_encoding=None):
        self._domain = domain
        self._default_encoding = default_encoding

    def __call__(self, ustr, default=None, context=None):
        """used for _()

        context - the message context (needed for language negotiation)
        ustr - the message id
        default - the default string if the message id isn't the default
        """
        return MessageID(ustr, domain=self._domain, default=default,
                   context=context, default_encoding=self._default_encoding)

InitializeClass(MessageIDFactory)