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
"""Topic and criterion interface

$Id: IATTopic.py,v 1.6 2004/05/14 12:04:07 godchap Exp $
""" 
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from interface import Interface, Attribute
from IATContentType import IATContentType

class IATTopic(IATContentType):
    """AT Topic marker interface
    """

    def listCriteriaTypes():
        """List available criteria types as dict
        """

    def listCriteriaMetaTypes():
        """List available criteria
        """

    def listSearchCriteriaTypes():
        """List available search criteria types as dict
        """

    def listSearchCriteriaMetaTypes():
        """List available search criteria
        """
    
    def listSortCriteriaTypes():
        """List available sort criteria types as dict
        """

    def listSortCriteriaMetaTypes():
        """List available sort criteria
        """
    
    def listCriteria():
        """Return a list of our criteria objects.
        """

    def listSearchCriteria():
        """Return a list of our search criteria objects.
        """

    def hasSortCriterion():
        """Tells if a sort criterai is already setup.
        """

    def getSortCriterion():
        """Return the Sort criterion if setup.
        """

    def removeSortCriterion():
        """remove the Sort criterion.
        """

    def setSortCriterion(field, reversed):
        """Set the Sort criterion.
        """

    def listAvailableFields():
        """Return a list of available fields for new criteria.
        """

    def listSubtopics():
        """Return a list of our subtopics.
        """

    def buildQuery():
        """Construct a catalog query using our criterion objects.
        """

    def queryCatalog(REQUEST=None, **kw):
        """Invoke the catalog using our criteria to augment any passed
            in query before calling the catalog.
        """

    def addCriterion(field, criterion_type):
        """Add a new search criterion.
        """

    def deleteCriterion(criterion_id):
        """Delete selected criterion.
        """

    def getCriterion(criterion_id):
        """Get the criterion object.
        """

    def addSubtopic(id):
        """Add a new subtopic.
        """


class IATTopicCriterion(Interface):
    """AT Topic Criterion interface
    """

    typeDescription = Attribute('''A short description used for the edit screen''')
    typeDescMsgId = Attribute('''The i18n msgid of the type description''')

    def widget(field_name, mode="view", field=None, **kwargs):
        """redefine widget() to allow seperate field_names from field
        """

    def getId():
        """get the objects id
        """

    def Type():
        """
        """

    def Description():
        """
        """

    def getCriteriaItems():
        """Return a sequence of items to be used to build the catalog query.
        """

class IATTopicSearchCriterion(IATTopicCriterion):
    """Interface for criteria used for searching
    """

class IATTopicSortCriterion(IATTopicCriterion):
    """Interface for criteria used for sorting
    """
