##############################################################################
#
# ATContentTypes http://sf.net/projects/collective/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2004 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic: 

$Id: __init__.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from UserDict import UserDict
from Products.Archetypes.public import registerType
from Products.ATContentTypes.config import *
 
class _CriterionRegistry(UserDict):
    """Registry for criteria """

    def register(self, criterion):
        id = criterion.meta_type
        self[id] = criterion
        registerType(criterion, PROJECTNAME)
        
    def listTypes(self):
        return self.keys()
        
CriterionRegistry = _CriterionRegistry()

# criteria
import ATDateCriteria
import ATListCriterion
import ATSimpleIntCriterion
import ATSimpleStringCriterion
import ATSortCriterion
