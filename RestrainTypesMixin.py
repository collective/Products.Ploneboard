#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
"""\
This module contains a mixin-class and a schema snippet to restrain types 
in a folder-instance

RCS-ID $Id: RestrainTypesMixin.py,v 1.2 2004/06/15 11:47:44 yenzenz Exp $
"""
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = 'Jens Klein <jens.klein@jensquadrat.de>'
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.Archetypes.public import *
from Products.ATContentTypes.interfaces.IRestrainTypes import IRestrainTypes
from config import *

schema = Schema((
    LinesField('RestrainedAllowedTypes',
        vocabulary='vocabularyPossibleTypes',
        enforceVocabulary=1,
        languageIndependent=1,
        write_permissions=RESTRAIN_TYPES_MIXIN_PERMISSION,                
        widget=MultiSelectionWidget(
            label='Set allowed types',
            visible = {'edit': 'visible', 'view': 'hidden'},
            label_msgid='label_restrain_allowed_types',
            description='Select one or more types, that should be allowed to '
                        'add inside this folder and its subfolders. Choose '
                        'nothing will allow all types.',
            description_msgid='description_restrain_allowed_types',
            i18n_domain='plone')
        ),
    ))

class RestrainTypesMixin:
    """ Gives the user with given rights the possibility to 
        restrain the addable types on per folder basis.
    """
    
    __implements__ = (IRestrainTypes)

    security = ClassSecurityInfo()
    
    def vocabularyPossibleTypes(self):
        """ returns a list of tuples in archetypes vocabulary style: 
            [(key,value),(key2,value2),...,(keyN,valueN)]
        """
        typetuples= [(fti.id, fti.title_or_id()) 
                     for fti in self._getPossibleTypes()]
        return DisplayList(typetuples)

    def _getPossibleTypes(self):
        """ returns a list of normally allowed objects as fti """

        tt = getToolByName(self,'portal_types')  
        fti = tt.getTypeInfo(self)
        fti.allowed_content_types
        if fti.filter_content_types:
            # take 'em from types tool
            return [tt[mt] for mt in fti.allowed_content_types]
        else:
            parent = aq_parent(self)
            if IRestrainTypes.isImplementedBy(parent):
                return parent.allowedContentTypes()
            else:
                return [fti for fti in tt.objectValues() if fti.globalAllow()]
    
    # overrides CMFCore's PortalFolder allowedTypes
    def allowedContentTypes(self):     
        """ returns restrained allowed types as list of fti's """
        tt = getToolByName(self,'portal_types')
        possible_ftis= self._getPossibleTypes()
        possible_mt  = [fti.id for fti in possible_ftis]        
        allowed      = list(self.getRestrainedAllowedTypes())
        possible_and_allowed = [tt[mt] for mt in allowed if mt in possible_mt]       
        return possible_and_allowed or possible_ftis
        
    # overrides CMFCore's PortalFolder invokeFactory
    security.declareProtected(AddPortalContent, 'invokeFactory')
    def invokeFactory( self, type_name, id, RESPONSE=None, *args, **kw):
        """ Invokes the portal_types tool """

        if not type_name in [fti.id for fti in self.allowedContentTypes()]:
            raise ValueError, 'Disallowed subobject type: %s' % type_name

        pt = getToolByName( self, 'portal_types' )
        apply( pt.constructContent,
               (type_name, self, id, RESPONSE) + args,
               kw )
            