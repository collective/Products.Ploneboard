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

$Id: ATPortalTypeCriterion.py,v 1.4 2004/08/22 21:43:07 tiran Exp $
"""

__author__  = 'Godefroid Chapelle'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    STRING_INDICES
from Products.ATContentTypes.interfaces.IATTopic import IATTopicSearchCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATPortalTypeCriterionSchema


class ATPortalTypeCriterion(ATBaseCriterion):
    """A portal_types criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'AT Portal Types Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'portal types values'

    security.declareProtected(CMFCorePermissions.View, 'getValue')
    def getValue(self):
        # refresh vocabulary
        types_tool = getToolByName(self, 'portal_types')
        portal_types = types_tool.listContentTypes()
        portal_types = [(portal_type, portal_type)
                        for portal_type in portal_types]
        self.schema['value'].vocabulary = DisplayList(list(portal_types))
        return self.getField('value').get(self)


    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.getValue() is not '':
            result.append((self.Field(), self.getValue()))

        return tuple(result)

registerCriterion(ATPortalTypeCriterion, STRING_INDICES)
