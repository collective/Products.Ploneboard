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

$Id: ATSortCriterion.py,v 1.8 2004/06/20 15:13:23 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    ALL_INDICES
from Products.ATContentTypes.interfaces.IATTopic import IATTopicSortCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATSortCriterionSchema


class ATSortCriterion(ATBaseCriterion):
    """A sort criterion"""

    __implements__ = BaseContentMixin.__implements__ + (IATTopicSortCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSortCriterionSchema
    meta_type      = 'ATSortCriterion'
    archetype_name = 'AT Sort Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Sort'
    
    def getCriteriaItems(self):
        result = [('sort_on', self.Field())]

        if self.getReversed():
            result.append(('sort_order', 'reverse'))

        return tuple(result)

registerCriterion(ATSortCriterion, ALL_INDICES)
