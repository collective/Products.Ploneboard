#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
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

"""This module contains a mixin-class and a schema snippet to constrain
which types can be added in a folder-instance

$Id: ConstrainTypesMixin.py,v 1.6 2004/09/13 05:39:55 runyaga Exp $
"""
__author__  = 'Jens Klein <jens.klein@jensquadrat.de>'
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import AddPortalContent

from Products.Archetypes.public import Schema
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import DisplayList

from Products.ATContentTypes.interfaces.IConstrainTypes import IConstrainTypes
from Products.ATContentTypes.config import CONSTRAIN_TYPES_MIXIN_PERMISSION

ConstrainTypesMixinSchema = Schema((
    LinesField('locallyAllowedTypes',
        vocabulary='vocabularyPossibleTypes',
        enforceVocabulary=True,
        languageIndependent=True,
        write_permissions=CONSTRAIN_TYPES_MIXIN_PERMISSION,
        widget=MultiSelectionWidget(
            label='Set allowed types',
            visible = {'edit': 'visible', 'view': 'hidden'},
            label_msgid='label_constrain_allowed_types',
            description='Select one or more types, that should be allowed to '
                        'add inside this folder and its subfolders. Choose '
                        'nothing will allow all types.',
            description_msgid='description_constrain_allowed_types',
            i18n_domain='plone')
        ),
    ))

class ConstrainTypesMixin:
    """ Gives the user with given rights the possibility to
        constrain the addable types on a per-folder basis.
    """

    __implements__ = IConstrainTypes

    security = ClassSecurityInfo()

    security.declarePrivate('vocabularyPossibleTypes')
    def vocabularyPossibleTypes(self):
        """returns a list of tuples in archetypes vocabulary style:

        [(key,value),(key2,value2),...,(keyN,valueN)]
        """
        typetuples= [(fti.title_or_id(), fti.id)
                     for fti in self._getPossibleTypes()]
        typetuples.sort()
        return DisplayList([(id, title) for title, id in typetuples])

    security.declarePrivate('recursiveGetLocallyAllowedTypes')
    def recursiveGetLocallyAllowedTypes(self):
        """get intersection of mine and my ancestors allowed types
        """
        typeIDs = self.getLocallyAllowedTypes()
        ancestors_allowed_types = self.ancestorsGetLocallyAllowedTypes()
        if ancestors_allowed_types:
            typeIDs = [typeID for typeID in typeIDs
                       if typeID in ancestors_allowed_types]
        return typeIDs

    security.declarePrivate('ancestorsGetLocallyAllowedTypes')
    def ancestorsGetLocallyAllowedTypes(self):
        """get all ancestors's allowed types, doing intersection
        """
        parent = aq_parent(self)
        try:
            # We don't check if the parent is an IConstrainTypes
            # because we want acquisition to work its magic.
            # The closest aq_parent that is an IConstrainTypes
            # will answer
            return parent.recursiveGetLocallyAllowedTypes()
        except AttributeError:
            # no parent in the acquisition chain is a Constrainer
            return ()

    def _getPossibleTypes(self):
        """returns a list of normally allowed objects as fti
        """

        tt = getToolByName(self,'portal_types')
        myfti = tt.getTypeInfo(self)
        # first we start with all available portal types.
        possible_ftis = tt.listTypeInfo()
        # then we only keep those that our fti allows
        if myfti.filter_content_types:
            possible_ftis = [fti for fti in possible_ftis
                             if myfti.allowType(fti.getId())]
        # then we try to find a types-constraint up the acquisition chain
        ancestors_allowed_types = self.ancestorsGetLocallyAllowedTypes()
        # if we find it, keep only the allowed types
        if ancestors_allowed_types:
            possible_ftis = [fti for fti in possible_ftis
                             if fti.getId() in ancestors_allowed_types]
        return possible_ftis

    # overrides CMFCore's PortalFolder allowedTypes
    def allowedContentTypes(self):
        """returns constrained allowed types as list of fti's
        """
        possible_ftis= self._getPossibleTypes()
        # getLocallyAllowedTypes is the accessor for the
        # the locallyAllowedTypes schema field.
        allowed = list(self.getLocallyAllowedTypes())
        possible_and_allowed = [fti for fti in possible_ftis
                                if fti.id in allowed]

	#Schwatzian Transform
        tmp = [(fti.title or fti.id, fti) for fti in possible_and_allowed]
	tmp.sort()
	possible_and_allowed = [fti[1] for fti in tmp]

        # if none are selected as allowed then all possible types
        # are allowed
        return possible_and_allowed or possible_ftis

    # overrides CMFCore's PortalFolder invokeFactory
    security.declareProtected(AddPortalContent, 'invokeFactory')
    def invokeFactory( self, type_name, id, RESPONSE=None, *args, **kw):
        """ Invokes the portal_types tool """
        if id in ('workspaces','homepage'): import pdb; pdb.set_trace()
        if not type_name in [fti.id for fti in self.allowedContentTypes()]:
            raise ValueError, 'Disallowed subobject type: %s' % type_name

        pt = getToolByName( self, 'portal_types' )
        args = (type_name, self, id, RESPONSE) + args
        pt.constructContent(*args, **kw)

InitializeClass(ConstrainTypesMixin)
