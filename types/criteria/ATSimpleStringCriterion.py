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

$Id: ATSimpleStringCriterion.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
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

class ATSimpleStringCriterion(ATBaseCriterion):
    """A simple string criterion"""

    security = ClassSecurityInfo()
    
    schema = schema
    meta_type = "AT Simple String Criterion"
    archetype_name = "AT Simple String Criterion"
    
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple( result )

CriterionRegistry.register(ATSimpleStringCriterion)
