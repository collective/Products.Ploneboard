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

$Id: ATSimpleIntCriterion.py,v 1.3 2004/03/29 07:21:01 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import CriterionRegistry
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.interfaces.IATTopic import IATTopicCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATSimpleIntCriterionSchema


class ATSimpleIntCriterion(ATBaseCriterion):
    """A simple int criterion"""

    security       = ClassSecurityInfo()
    schema         = ATSimpleIntCriterionSchema
    meta_type      = 'ATSimpleIntCriterion'
    archetype_name = 'AT Simple Int Criterion'

    def getCriteriaItems(self):
        result = []

        if self.Value() or self.Value() == 0:
            result.append((self.Field(), self.Value()))

        return tuple(result)

CriterionRegistry.register(ATSimpleIntCriterion)
