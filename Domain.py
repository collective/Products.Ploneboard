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

$Id: Domain.py,v 1.1 2003/01/02 15:29:12 lalo Exp $
"""

class Domain:

    def __init__(self, domain, service):
        self._domain = domain
        self._translationService = service

    def getDomainName(self):
        """Return the domain name"""
        return self._domain
    

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None):
        return self._translationService.translate(
            self._domain, msgid, mapping, context, target_language)
