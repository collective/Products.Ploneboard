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

$Id: schemata.py,v 1.2 2004/04/09 22:02:21 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.Archetypes.Marshall import RFC822Marshaller, PrimaryFieldMarshaller
from Products.ATContentTypes.Permissions import ChangeTopics

###
# DateCriteria vocabularies
###

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
                                description="Should not contain spaces, underscores or mixed case. "\
                                            "Short Name is part of the item's web address.",
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
                                label_msgid="label_criterion_field_name",
                                description="Should not contain spaces, underscores or mixed case. "\
                                            "Short Name is part of the item's web address.",
                                description_msgid="help_criterion_field_name",
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
                                label="Value name",
                                label_msgid="label_date",
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
                                label="Value name",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
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
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
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
                                label="Value name",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
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
                default=None,
                widget=StringWidget(
                                label="Value name",
                                #label_msgid="label_criterion_field_name",
                                #description="Should not contain spaces, underscores or mixed case. "\
                                #            "Short Name is part of the item's web address.",
                                #description_msgid="help_criterion_field_name",
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
