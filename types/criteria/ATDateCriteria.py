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

$Id: ATDateCriteria.py,v 1.8 2004/06/01 09:10:52 zworkb Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    ALL_INDICES, DATE_INDICES, STRING_INDICES, LIST_INDICES
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.interfaces.IATTopic import IATTopicSearchCriterion
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATDateCriteriaSchema


class ATDateCriteria(ATBaseCriterion):
    """A date criteria"""


    __implements__ = BaseContentMixin.__implements__ + (IATTopicSearchCriterion, )

    security       = ClassSecurityInfo()
    schema         = ATDateCriteriaSchema
    meta_type      = 'ATFriendlyDateCriteria'
    archetype_name = 'AT Friendly Date Criteria'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'exact date value'
    
    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """Return a sequence of items to be used to build the catalog query.
        """
        if self.value is not None:
            field = self.Field()
            value = self.Value()

            # Negate the value for 'old' days
            if self.getDateRange() == '-':
                value = -value

            date = DateTime() + value

            operation = self.getOperation()
            if operation == 'within_day':
                range = ( date.earliestTime(), date.latestTime() )
                return ( ( field, {'query': range, 'range': 'min:max'} ), )
            else:
                return ( ( field, {'query': date, 'range': operation} ), )
        else:
            return ()

registerCriterion(ATDateCriteria, DATE_INDICES)
