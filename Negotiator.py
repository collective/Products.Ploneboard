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
"""

$Id: Negotiator.py,v 1.6 2003/11/20 21:16:08 longsleep Exp $
"""

try:
    True
except NameError:
    True=1
    False=0


_langPrefsRegistry = {}

def getAcceptedHelper(self, request, kind='language'):
    # this is patched on prefs classes which dont define the getAccepted classes
    # but define the deprecated getPreferredLanguages method
    return self.getPreferredLanguages()

def registerLangPrefsMethod(prefs, kind='language'):
    # check for correct format of prefs
    if type(prefs) is not type({}): prefs = {'klass':prefs,'priority':0}
    # add chain for kind
    if not _langPrefsRegistry.has_key(kind): _langPrefsRegistry[kind]=[]
    # backwards compatibilty monkey patch
    if not hasattr(prefs['klass'], 'getAccepted'): prefs['klass'].getAccepted = getAcceptedHelper
    # add this pref helper
    _langPrefsRegistry[kind].append(prefs)
    # sort by priority
    _langPrefsRegistry[kind].sort(lambda x, y: cmp(x['priority'], y['priority']))

def getLangPrefsMethod(env, kind='language'):
    # get higest prio method for kind
    return _langPrefsRegistry[kind][-1]['klass'](env)

def lang_normalize(lang):
    return lang.replace('_', '-')

def str_lower(aString):
    return aString.lower()

def type_accepted(available, preferred):
    # ex: preferred is text/* and available is text/html
    av = available.split('/')
    pr = preferred.split('/')
    if len(av) < 2 or len(pr) < 2:
        return False
    return pr[1] == '*' and pr[0] == av[0]

def lang_accepted(available, preferred):
    # ex: available is pt, preferred is pt-br
    return available.startswith(preferred)

def _false(*a, **kw):
    pass


class BrowserAccept:

    filters = {
        'content-type': (str_lower,),
        'language': (str_lower, lang_normalize),
    }

    def __init__(self, request):
        pass

    def getAccepted(self, request, kind='content-type'):
        get = request.get
        custom_name = ('user_%s' % kind).lower()
        if kind == 'content-type':
            header_name = ('HTTP_ACCEPT').upper()
        else:
            header_name = ('HTTP_ACCEPT_%s' % kind).upper()

        try:
            user_accepts = get(custom_name, '')
            http_accepts = get(header_name, '')
        except:
            from traceback import print_exc
            print_exc()
            return
        if user_accepts and http_accepts and user_accepts == request.cookies.get('custom_name'):
            user_accepts = [a.strip() for a in user_accepts.split(',')]
            http_accepts = [a.strip() for a in http_accepts.split(',')]
            for l in user_accepts:
                if l not in http_accepts:
                    req_accepts = user_accepts + http_accepts
                    break
                else:
                    # user_accepts is a subset of http_accepts
                    request.RESPONSE.expireCookie('custom_name', path='/')
                    req_accepts = http_accepts
        else:
            req_accepts = (user_accepts +','+ http_accepts).split(',')

        accepts = []
        i=0
        length=len(req_accepts)
        filters = self.filters.get(kind, ())

        # parse quality strings and build a tuple 
        # like ((float(quality), lang), (float(quality), lang))
        # which is sorted afterwards
        # if no quality string is given then the list order
        # is used as quality indicator
        for accept in req_accepts:
            for normalizer in filters:
                accept = normalizer(accept)
            if accept:
                l = accept.split(';', 2)
                quality = []

                if len(l) == 2:
                    try:
                        q = l[1]
                        if q.startswith('q='):
                            q = q.split('=', 2)[1]
                            quality = float(q)
                    except:
                        pass

                if quality == []:
                    quality = float(length-i)

                accepts.append((quality, l[0]))
                i += 1

        # sort and reverse it
        accepts.sort()
        accepts.reverse()

        return [accept[1] for accept in accepts]


registerLangPrefsMethod({'klass':BrowserAccept,'priority':10 }, 'language')
registerLangPrefsMethod({'klass':BrowserAccept,'priority':10 }, 'content-type')


class Negotiator:

    tests = {
        'content-type': type_accepted,
        'language': lang_accepted,
    }

    def negotiate(self, choices, request, kind='content-type'):
        choices = tuple(choices)
        cache_name = '_pts_negotiator_cache_%s' % kind
        try:
            cache = request.other[cache_name]
        except KeyError:
            # Store cache in request object
            cache = {}
            request.set(cache_name, cache)
        try:
            return cache[choices]
        except KeyError:
            cache[choices] = self._negotiate(choices, request, kind)
            return cache[choices]

    def _negotiate(self, choices, request, kind):
        
        envprefs = getLangPrefsMethod(request, kind)
        userchoices = envprefs.getAccepted(request, kind)
        # Prioritize on the user preferred choices.  Return the first user
        # preferred choice that the object has available.
        test = self.tests.get(kind, _false)
        for choice in userchoices:
            if choice in choices:
                return choice
            for l_avail in choices:
                if test(l_avail, choice):
                    return l_avail
        return None

    # backwards compatibility... should be deprecated
    def getLanguage(self, langs, request):
        return self.negotiate(langs, request, 'language')

    def getLanguages(self, request):
        envprefs = getLangPrefsMethod(request, 'language')
        return envprefs.getAccepted(request, 'language')


negotiator = Negotiator()

def negotiate(langs, request):
    return negotiator.negotiate(langs, request, 'language')

