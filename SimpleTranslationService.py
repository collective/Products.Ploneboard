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
"""This is a simple implementation of the ITranslationService interface.

$Id: SimpleTranslationService.py,v 1.1 2003/01/02 15:29:12 lalo Exp $
"""

import re
from types import DictType, StringType, UnicodeType
from Negotiator import Negotiator
from Domain import Domain
from pax import XML

# Setting up some regular expressions for finding interpolation variables in
# the text.
NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_interp_regex = re.compile(r'(?<!\$)(\$(?:%(n)s|{%(n)s}))' %({'n': NAME_RE}))
_get_var_regex = re.compile(r'%(n)s' %({'n': NAME_RE}))


def map_get(map, name):
    return map.get(name)

def obj_get(obj, name):
    return getattr(obj, name)

class SimpleTranslationService:
    """This is the simplest implementation of the ITranslationInterface I
       could come up with.

       The constructor takes one optional argument 'messages', which will be
       used to do the translation. The 'messages' attribute has to have the
       following structure:

       {('domain', 'language', 'msg_id'): 'message', ...}

       Note: This Translation Service does not implemen
    """

    def __init__(self, messages=None):
        """Initializes the object. No arguments are needed."""
        if messages is None:
            self.messages = {}
        else:
            assert type(messages) == DictType
            self.messages = messages


    def translate(self, domain, msgid, mapping=None, context=None,
                  target_language=None):
        """
        """
        # Find out what the target language should be
        if target_language is None:
            if context is None:
                raise TypeError, 'No destination language'
            else:
                langs = [m[1] for m in self.messages.keys()]
                # Let's negotiate the language to translate to. :)
                negotiator = Negotiator()
                target_language = negotiator.getLanguage(langs, context)

        # Make a raw translation without interpolation
        text = self.messages.get((domain, target_language, msgid), msgid)

        # Now we need to do the interpolation
        return self.interpolate(text, mapping)


    def getDomain(self, domain):
        """
        """
        return Domain(domain, self)

    #
    ############################################################


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
            get = obj_get

        # Find all the spots we want to substitute
        to_replace = _interp_regex.findall(text)

        # Now substitute with the variables in mapping
        for string in to_replace:
            var = _get_var_regex.findall(string)[0]
            value = get(mapping, var)
            if callable(value):
                value = value()
            if value is None:
                value = string
            if type(value) not in (StringType, UnicodeType):
                # FIXME: we shouldn't do this. We should instead
                # return a list. But i'm not sure about how to use
                # the regex to split the text.
                value = XML(value)
            text = text.replace(string, value)

        return text
     except:
        import traceback
        traceback.print_exc()
