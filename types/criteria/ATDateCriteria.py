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

$Id: ATDateCriteria.py,v 1.2 2004/03/13 19:14:03 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.types.criteria import CriterionRegistry
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.config import *
from ATBaseCriterion import ATBaseCriterion, ATBaseCriterionSchema

DateOptions = DisplayList((
                    (     0, 'Now'      )
                  , (     1, '1 Day'    )
                  , (     2, '2 Days'   )
                  , (     5, '5 Days'   )
                  , (     7, '1 Week'   )
                  , (    14, '2 Weeks'  )
                  , (    31, '1 Month'  )
                  , (  31*3, '3 Months' )
                  , (  31*6, '6 Months' )
                  , (   365, '1 Year'   )
                  , ( 365*2, '2 years'  )
    ))

CompareOperations = DisplayList((
                    ('min', 'min')
                  , ('max', 'max')
                  , ('within_day', 'within_day')
    ))

RangeOperations = DisplayList((
                    ('-', 'old')
                  , ('+', 'ahead')
    ))

schema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                accessor="Value",
                mutator="setValue",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=DateOptions,
                widget=SelectionWidget(
                                label="Value name",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
                                i18n_domain="plone"),
                ),
    StringField('operation',
                required=1,
                mode="rw",
                default=None,
                write_permission=ChangeTopics,
                vocabulary=CompareOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                                label="operation name",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
                                i18n_domain="plone"),
                ),
    StringField('dateRange',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=RangeOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                                label="date range",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
                                i18n_domain="plone"),
                ),
    ))

class ATDateCriteria(ATBaseCriterion):
    """A date criteria"""

    security       = ClassSecurityInfo()
    schema         = schema
    meta_type      = 'ATFriendlyDateCriteria'
    archetype_name = 'AT Friendly Date Criteria'
    
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

CriterionRegistry.register(ATDateCriteria)
