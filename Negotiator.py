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
"""

$Id: Negotiator.py,v 1.2 2003/01/03 17:38:34 dreamcatcher Exp $
"""

_langPrefsRegistry = []

def registerLangPrefsMethod(prefs):
    if type(prefs) is not type({}):
        prefs = {'klass':prefs,'priority':0}
    _langPrefsRegistry.append(prefs)
    _langPrefsRegistry.sort(lambda x, y: cmp(x['priority'], y['priority']))

def getLangPrefsMethod(env):
    return _langPrefsRegistry[-1]['klass'](env)

class DummyUserPreferredLanguages:

    def __init__(self, env):
        self._env = env

    def getPreferredLanguages(self):
        return self._env.getPreferredLanguages()

registerLangPrefsMethod(DummyUserPreferredLanguages)

class BrowserLanguages:
    
    def __init__(self, context):
        try:
            # ZPT, contrary to the spec, doesn't pass the request
            # as context arg
            get = context.REQUEST.get
        except AttributeError:
            get = context.get
            
        try:
            req_langs = get('user_language', None) or \
                        get('HTTP_ACCEPT_LANGUAGE', '')
        except:
            from traceback import print_exc
            print_exc()
            self.langs = ()
            return
	langs = []
	for lang in req_langs.split(','):
	    lang = lang.strip().lower().replace('_', '-')
	    if lang:
		langs.append(lang.split(';')[0])
        self.langs = langs
	
    def getPreferredLanguages(self):
	"""
	"""
	return self.langs
		
registerLangPrefsMethod({'klass':BrowserLanguages,'priority':10 })

class Negotiator:


    def getLanguage(self, langs, env):
        envprefs = getLangPrefsMethod(env)
        userlangs = envprefs.getPreferredLanguages()
        # Prioritize on the user preferred languages.  Return the first user
        # preferred language that the object has available.
        for lang in userlangs:
            if lang in langs:
                return lang
        return None

    def getLanguages(self, env):
        envprefs = getLangPrefsMethod(env)
        return envprefs.getPreferredLanguages()


negotiator = Negotiator()
