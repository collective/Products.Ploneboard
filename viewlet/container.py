##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Folder containing viewlets.

$Id: container.py,v 1.4 2004/06/22 07:47:46 godchap Exp $
"""
from Products.Archetypes.public import *
from Products.CompositePack.config import PROJECTNAME
from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import UniqueObject

class ViewletContainer(BaseFolderMixin, UniqueObject):
    """A basic, Archetypes-based Composite Element
    that uses references instead of path, and a dropdown
    for selecting templates
    """
    meta_type = portal_type = archetype_name = 'CompositePack Viewlet Container'
    schema = MinimalSchema
    global_allow = 0

    def all_meta_types(self):
        return BaseFolderMixin.all_meta_types(
            self, interfaces=(IViewlet,))

registerType(ViewletContainer, PROJECTNAME)
