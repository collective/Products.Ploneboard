##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""CompositePack Viewlet :
   placeholder for a method found by acquisition
   this method is used to display a composite element.
   

$Id: __init__.py,v 1.4 2004/06/22 07:47:46 godchap Exp $
"""
from Products.Archetypes.public import *
from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CompositePack.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName

class Viewlet(BaseContentMixin):

    __implements__ = BaseContent.__implements__ + (IViewlet,)

    meta_type = portal_type = archetype_name = 'CompositePack Viewlet'
    global_allow = 0

    schema = MinimalSchema + Schema((
        StringField(
        'skin_method',
        widget=StringWidget(label='Skin Method',
                            description=('Method called for rendering '
                                         'the viewlet/layout.'))
        ),
        ))


    def getTemplate(self):
        """ Return the template """
        purl = getToolByName(self, 'portal_url')
        portal = purl.getPortalObject()
        return portal.restrictedTraverse(self.getSkin_method())

registerType(Viewlet, PROJECTNAME)
