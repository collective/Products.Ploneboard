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
"""

$Id: schemata.py,v 1.9 2005/01/24 18:27:06 tiran Exp $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.ATContentTypes.Permissions import ChangeTopics

###
# DateCriteria vocabularies
###

DateOptions = DisplayList((
                    (     str(0), 'Now'      )
                  , (     str(1), '1 Day'    )
                  , (     str(2), '2 Days'   )
                  , (     str(5), '5 Days'   )
                  , (     str(7), '1 Week'   )
                  , (    str(14), '2 Weeks'  )
                  , (    str(31), '1 Month'  )
                  , (  str(31*3), '3 Months' )
                  , (  str(31*6), '6 Months' )
                  , (   str(365), '1 Year'   )
                  , ( str(365*2), '2 Years'  )
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

###
# ListCriterion vocabularies
###

CompareOperators = DisplayList((
                    ('and', 'and')
                  , ('or', 'or')
    ))

###
# AT Base Criterion
###

ATBaseCriterionSchema = Schema((
    StringField('id',
                required=1,
                mode="r",
                default=None,
                write_permission=ChangeTopics,
                widget=IdWidget(
                    label="Short Name",
                    label_msgid="label_short_name",
                    description=("Should not contain spaces, underscores or mixed case. "
                                 "Short Name is part of the item's web address."),
                    description_msgid="help_shortname",
                    visible={'view' : 'invisible'},
                    i18n_domain="plone"),
                ),
    StringField('field',
                required=1,
                mode="r",
                accessor="Field",
                write_permission=ChangeTopics,
                default=None,
                widget=StringWidget(
                    label="Field name",
                    label_msgid="label_criteria_field_name",
                    description=("Should not contain spaces, underscores or mixed case. "
                                 "Short Name is part of the item's web address."),
                    description_msgid="help_criteria_field_name",
                    i18n_domain="plone"),
                ),

    ))

###
# AT Date Criteria
###

ATDateCriteriaSchema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                accessor="Value",
                mutator="setValue",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=DateOptions,
                widget=SelectionWidget(
                    label="Date",
                    label_msgid="label_date_criteria_value",
                    description="Reference date",
                    description_msgid="help_date_criteria_value",
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
                    label="Operation name",
                    label_msgid="label_date_criteria_operation",
                    description="Operation applied to the values",
                    description_msgid="help_date_criteria_operation",
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
                    label_msgid="label_date_criteria_range",
                    description="Specify if the range is ahead of "
                    "the reference date or not.",
                    description_msgid="help_date_criteria_range",
                    i18n_domain="plone"),
                ),
    ))

###
# AT List Criterion
###

ATListCriterionSchema = ATBaseCriterionSchema + Schema((
    LinesField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=[],
                widget=LinesWidget(
                    label="Values",
                    label_msgid="label_list_criteria_value",
                    description="Values, each on its own line.",
                    description_msgid="help_list_criteria_value",
                    i18n_domain="plone"),
                ),
    StringField('operator',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default='or',
                vocabulary=CompareOperators,
                widget=SelectionWidget(
                    label="operator name",
                    label_msgid="label_list_criteria_operator",
                    description="Operator used to join the tests "
                    "on each value.",
                    description_msgid="help_list_criteria_operator",
                    i18n_domain="plone"),
                ),
    ))

###
# AT Simple Int Criterion
###

ATSimpleIntCriterionSchema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=None,
                widget=IntegerWidget(
                    label="Value",
                    label_msgid="label_int_criteria_value",
                    description="An integer number.",
                    description_msgid="help_int_criteria_value",
                    i18n_domain="plone"),
                ),

    ))

###
# AT Simple String Criterion
###

ATSimpleStringCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default="",
                widget=StringWidget(
                    label="Value",
                    label_msgid="label_string_criteria_value",
                    description="A string value.",
                    description_msgid="help_string_criteria_value",
                    i18n_domain="plone"),
                ),

    ))

###
# AT Portal Types Criterion
###

ATPortalTypeCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="getValue",
                mutator="setValue",
                default=None,
                widget=MultiSelectionWidget(
                    label="Value",
                    label_msgid="label_portal_type_criteria_value",
                    description="One of the registered portal types.",
                    description_msgid="help_portal_type_criteria_value",
                    i18n_domain="plone"),
                ),

    ))


###
# AT Sort Criterion
###

ATSortCriterionSchema = ATBaseCriterionSchema + Schema((
    BooleanField('reversed',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                default=0,
                widget=BooleanWidget(
                    label="Reverse",
                    #label_msgid="label_criterion_field_name",
                    #description="Should not contain spaces, underscores or mixed case. "\
                    #            "Short Name is part of the item's web address.",
                    #description_msgid="help_criterion_field_name",
                    i18n_domain="plone"),
                ),

    ))
