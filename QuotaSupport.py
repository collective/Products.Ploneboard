#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
""" Quota Support


"""
__author__  = 'Christian Heimes, Christian Theune'
__docformat__ = 'restructuredtext'

from Acquisition import aq_parent, aq_explicit
from Globals import InitializeClass

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *

from Products.ATContentTypes.config import *
from Products.ATContentTypes.interfaces.IQuotaSupport import IQuotaSupport

from zExceptions import Forbidden

class QuotaException(Forbidden):
    pass

quotaSupportSchema = Schema((
    BooleanField('enableQuota',
                write_permission=CMFCorePermissions.ManagePortal,
                widget=BooleanWidget(
                    description="",
                    description_msgid = "",
                    label = "Enable quota support",
                    label_msgid = "",
                    i18n_domain = "plone",
                )),
    IntegerField('quotaMaxObjects',
                write_permission=CMFCorePermissions.ManagePortal,
                widget=IntegerWidget(
                    description="",
                    description_msgid = "",
                    label = "Max objects",
                    label_msgid = "",
                    i18n_domain = "plone",
                )),
    IntegerField('quotaMaxSize',
                write_permission=CMFCorePermissions.ManagePortal,
                widget=IntegerWidget(
                    description="",
                    description_msgid = "",
                    label = "Max size",
                    label_msgid = "",
                    i18n_domain = "plone",
                )),
    ))

class BaseQuotaSupportMixin:
    """Quota support mixin class for ATCTOrderedFolder
    
    This mixin can be used to restrict the amount or size of subobjects inside
    a folder based on Archetypes.
    
    XXX Really just an idea. Maybe I'll find some time and sponsors to finish
    it. :)
    """

    __implements__ = IQuotaSupport

    security = ClassSecurityInfo()

    #actions = ({
    #    'id'          : 'quota',
    #    'name'        : 'Quota',
    #    'action'      : 'string:${object_url}/atct_quota',
    #    'permissions' : (CMFCorePermissions.ManagePortal, )
    #     },
    #)

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'getContentSizeAndAmount')
    def getContentSizeAndAmount(self, **kwargs):
        """Get the size and amount of all objects
        """
        raise NotImplementedError
    
InitializeClass(QuotaSupportMixin)


class CatalogQuotaSupportMixin(BaseSupportMixin):
    """QuotaSupport implementation using the portal catalog
    """
    
    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'getContentSizeAndAmount')
    def getContentSizeAndAmount(self, **kwargs):
        """Get the size and amount of all objects
        
        using the portal catalog to speed up the lookup
        """
        cat = getToolByName(self, 'portal_catalog')
        brains = cat(path=self.getPhysicalPath())
        amount = len(brains)
        size = 0
        for brain in brains:
            try:
                s = int(brain.get_size)
            except TypeError:
                pass
            else:
                size+=s
        return (size, amount, )

InitializeClass(CatalogQuotaSupportMixin)

QuotaSupportMixin = CatalogQuotaSupportMixin

__all__ = ('CatalogQuotaSupportMixin', )
