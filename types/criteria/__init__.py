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

$Id: __init__.py,v 1.12 2004/12/23 15:16:17 tesdal Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from UserDict import UserDict
from Products.Archetypes.public import registerType
from Products.ATContentTypes.config import *
from types import StringType

from Products.ATContentTypes.interfaces.IATTopic import IATTopicSearchCriterion, IATTopicSortCriterion

ALL_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex', 'KeywordIndex',
               'PathIndex', 'TextIndex', 'TextIndexNG2', 'TopicIndex',
               'ZCTextIndex', 'NavtreeIndexNG', 'ExtendedPathIndex')

SORT_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex', 'KeywordIndex')
# TextIndex, PathIndex, TopicIndex, ZCTextIndex, TextIndexNG2, NavtreeIndexNG
# are not usable to sort
# as they do not have 'keyForDocument' attribute

DATE_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex')

STRING_INDICES = ('FieldIndex', 'KeywordIndex', 'PathIndex', 'TextIndex',
                  'TextIndexNG2', 'ZCTextIndex', 'NavtreeIndexNG', 'ExtendedPathIndex')

LIST_INDICES = ('FieldIndex', 'KeywordIndex', )

class _CriterionRegistry(UserDict):
    """Registry for criteria """

    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)
        self.index2criterion = {}
        self.criterion2index = {}

    def register(self, criterion, indices):
        if type(indices) is StringType:
            indices = (indices,)
        indices = tuple(indices)

        if indices == ():
            indices = ALL_INDICES

        id = criterion.meta_type
        self[id] = criterion

        self.criterion2index[id] = indices
        for index in indices:
            value = self.index2criterion.get(index, ())
            self.index2criterion[index] = value + (id,)

        registerType(criterion, PROJECTNAME)

    def unregister(self, criterion):
        id = criterion.meta_type
        self.pop(id)
        self.criterion2index.pop(id)
        for (index, value) in self.index2criterion.items():
            if id in value:
                valuelist = list(value)
                del valuelist[valuelist.index(id)]
                self.index2criterion[index] = tuple(valuelist)

    def listTypes(self):
        return self.keys()

    def listSortTypes(self):
        return [key for key in self.keys()
                    if IATTopicSortCriterion.isImplementedByInstancesOf(self[key])]

    def listSearchTypes(self):
        return [key for key in self.keys()
                    if IATTopicSearchCriterion.isImplementedByInstancesOf(self[key])]

    def listCriteria(self):
        return self.values()

    def indicesByCriterion(self, criterion):
        return self.criterion2index[criterion]

    def criteriaByIndex(self, index):
        return self.index2criterion[index]

CriterionRegistry = _CriterionRegistry()
registerCriterion = CriterionRegistry.register
unregisterCriterion = CriterionRegistry.unregister

__all__ = ('registerCriterion', 'ALL_INDICES', 'DATE_INDICES', 'STRING_INDICES',
           'LIST_INDICES', )

# criteria
import ATDateCriteria
import ATListCriterion
import ATSimpleIntCriterion
import ATSimpleStringCriterion
import ATPortalTypeCriterion
import ATSortCriterion
