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

$Id: ATPortalTypeCriterion.py,v 1.1 2004/05/30 14:13:40 godchap Exp $
"""

__author__  = 'Godefroid Chapelle'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.TypesTool import TypesTool
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    ALL_INDICES, DATE_INDICES, STRING_INDICES, LIST_INDICES
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.interfaces.IATTopic import IATTopicSearchCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATPortalTypeCriterionSchema


class ATPortalTypeCriterion(ATBaseCriterion):
    """A portal_types criterion"""

    __implements__ = BaseContentMixin.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'AT Portal Types Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'portal types values'

    def getValue(self):
        # refresh vocabulary
        types_tool = getToolByName(self, TypesTool.id)
        portal_types = types_tool.listContentTypes()
        portal_types = [(portal_type, portal_type)
                        for portal_type in portal_types]
        self.schema['value'].vocabulary = DisplayList(list(portal_types))
        return self.getField('value').get(self)
      
    
    def getCriteriaItems(self):
        result = []

        if self.getValue() is not '':
            result.append((self.Field(), self.getValue()))

        return tuple( result )

registerCriterion(ATPortalTypeCriterion, STRING_INDICES)
