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

$Id: ATBaseCriterion.py,v 1.11 2004/08/22 21:43:07 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import BaseContentMixin

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.criteria import registerCriterion, \
    ALL_INDICES, DATE_INDICES, STRING_INDICES, LIST_INDICES
from Products.ATContentTypes.interfaces.IATTopic import IATTopicCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema


class ATBaseCriterion(BaseContentMixin):
    """A basic criterion"""

    __implements__ = BaseContentMixin.__implements__ + (IATTopicCriterion, )
    security = ClassSecurityInfo()

    schema = ATBaseCriterionSchema
    meta_type = 'ATBaseCriterion'
    archetype_name = 'Base Criterion'
    typeDescription= ''
    typeDescMsgId  = ''
    global_allow = 0

    def __init__(self, id, field=None):
        self.getField('id').set(self, id) # set is ok
        self.getField('field').set(self, field)

    security.declareProtected(CMFCorePermissions.View, 'getId')
    def getId(self):
        """Get the object id"""
        return str(self.id)

    def setId(self, value, *kw):
        """Setting a new ID isn't allowed
        """
        assert value == self.getId(), 'You are not allowed to change the id'

    security.declareProtected(CMFCorePermissions.View, 'Type')
    def Type(self):
        return self.archetype_name

    security.declareProtected(CMFCorePermissions.View, 'Description')
    def Description(self):
        lines = [ line.strip() for line in self.__doc__.splitlines() ]
        return ' '.join( [ line for line in lines if line ] )

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """Return a sequence of items to be used to build the catalog query.
        """
        raise NotImplementedError

InitializeClass(ATBaseCriterion)
# registerCriterion(ATBaseCriterion, ())
