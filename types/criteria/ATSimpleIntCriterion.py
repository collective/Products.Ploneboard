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

$Id: ATSimpleIntCriterion.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
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

schema = ATBaseCriterionSchema + Schema((
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

class ATSimpleIntCriterion(ATBaseCriterion):
    """A simple int criterion"""

    security = ClassSecurityInfo()
    
    schema = schema
    meta_type = "AT Simple Int Criterion"
    archetype_name = "AT Simple Int Criterion"            
    
    def getCriteriaItems(self):
        result = []

        if self.Value() or self.Value() == 0:
            result.append((self.Field(), self.Value()))

        return tuple(result)

CriterionRegistry.register(ATSimpleIntCriterion)
