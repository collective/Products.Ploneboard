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

$Id: ATListCriterion.py,v 1.2 2004/03/13 19:14:03 tiran Exp $
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

CompareOperators = DisplayList((
                    ('and', 'and')
                  , ('or', 'or')
    ))

schema = ATBaseCriterionSchema + Schema((
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

class ATListCriterion(ATBaseCriterion):
    """A list criterion"""

    security       = ClassSecurityInfo()
    schema         = schema
    meta_type      = 'ATListCriterion'
    archetype_name = 'AT List Criterion'
    
    def getCriteriaItems(self):
        # filter out empty strings
        result = []

        value = tuple([ value for value in self.Value() if value ])
        if not value:
            return ()
        result.append((self.Field(), value),)
        result.append(('%s_operator' % self.Field(), self.getOperator()))

        return tuple(result)

CriterionRegistry.register(ATListCriterion)
