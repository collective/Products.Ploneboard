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

$Id: ATBaseCriterion.py,v 1.1 2004/03/08 10:48:41 tiran Exp $
"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.Archetypes.public import *
from Products.Archetypes.BaseContent import BaseContentMixin
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Renderer import renderer

from Products.ATContentTypes.types.criteria import CriterionRegistry
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IATTopic import IATTopicCriterion

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

class ATBaseCriterion(BaseContentMixin):
    """A basic criterion"""

    __implements__ = BaseContentMixin.__implements__ + (IATTopicCriterion, )
    security = ClassSecurityInfo()
    
    schema = ATBaseCriterionSchema
    meta_type = "AT Base Criterion"
    archetype_name = "Base Criterion"            
    global_allow = 0
    
    def __init__(self, id, field=None):
        self.getField('id').set(self, id)
        self.getField('field').set(self, field)

    security.declareProtected(CMFCorePermissions.View, 'widget')
    def widget(self, field_name, mode="view", field=None, **kwargs):
        """redefine widget() to allow seperate field_names from field """
        if not field:
            field = self.Schema()[field_name]
        widget = field.widget
        return renderer.render(field_name, mode, widget, self, field=field,
                               **kwargs)

    security.declareProtected(CMFCorePermissions.View, 'getId')
    def getId(self):
        """get the objects id"""
        return str(self.id)

    security.declareProtected(CMFCorePermissions.View, 'Type')
    def Type(self):
        return self.archetype_type

    security.declareProtected(CMFCorePermissions.View, 'Description')
    def Description(self):
        lines = [ line.strip() for line in self.__doc__.splitlines() ]
        return ' '.join( [ line for line in lines if line ] )

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """Return a sequence of items to be used to build the catalog query.
        """
        raise NotImplementedError        

# CriterionRegistry.register(ATBaseCriterion)
