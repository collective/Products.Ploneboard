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

$Id: ATListCriterion.py,v 1.8 2004/06/20 15:13:23 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    STRING_INDICES
from Products.ATContentTypes.interfaces.IATTopic import IATTopicSearchCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATListCriterionSchema


class ATListCriterion(ATBaseCriterion):
    """A list criterion"""

    __implements__ = BaseContentMixin.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATListCriterionSchema
    meta_type      = 'ATListCriterion'
    archetype_name = 'AT List Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'logical AND or OR of list values'
    
    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        # filter out empty strings
        result = []

        value = tuple([ value for value in self.Value() if value ])
        if not value:
            return ()
        result.append((self.Field(), value),)
        result.append(('%s_operator' % self.Field(), self.getOperator()))

        return tuple(result)

registerCriterion(ATListCriterion, STRING_INDICES)
