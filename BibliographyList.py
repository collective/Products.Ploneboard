##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

""" BibliographyList: personal list of bibliographic references
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList, registerType
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import ReferenceField, ReferenceWidget
from Products.Archetypes.public import StringField, SelectionWidget
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

# possible types of bibliographic references from module 'CMFBibliographyAT'
from Products.CMFBibliographyAT.config import REFERENCE_TYPES as search_types

from config import LISTING_VALUES

class BibrefListWidget(BibrefListWidget):
    """ custom widget for TTW references input handling """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "widget_bibreflist",
        })

registerWidget(ReferencesWidget)

schema = BaseSchema + Schema((
    ReferenceField('references_list',
                   multiValued=1,
                   relationship='lists reference',
                   widget=BibrefListWidget(label="References",
                                           label_msgid="label_references_list",
                                           description_msgid="help_references_list",
                                           i18n_domain="plone",
                                           description="Search and select references to add to the list or organize/remove listed references.",
                                           ),
                   ),
    StringField('PresentationStyle',
                multiValued=0,
                default = 'stl_minimal',
                vocabulary="vocabCustomStyle",
                enforce_vocabulary=1,
                widget=SelectionWidget(label="Presentation Style",
                              label_msgid="label_presentation",
                              description_msgid="help_presentation",
                              description="Select the format how you want to present your list.",           
                              i18n_domain="plone",
                              format="select",
                              visible={'edit':'visible','view':'invisible'},),
                ),
    StringField('ListingLayout',
                multiValued=0,
                default = 'bulletted',
                vocabulary=LISTING_VALUES,
                enforce_vocabulary=1,
                widget=SelectionWidget(label="Listing Layout",
                              label_msgid="label_bibliolist_listing_format",
                              description_msgid="help_bibliolist_listing_format",
                              description="How the list will be rendered in the view page.",           
                              i18n_domain="plone",
                              format="radio",
                              visible={'edit':'visible','view':'invisible'},),
                ),
    ))

class BibliographyList(BaseContent):
    """ Bibliography list class 
    """

    archetype_name = "Bibliography List"

    global_allow = 1
    content_icon = 'biblist_icon.gif'

    schema = schema

    actions = (
        {'id'          : 'listdownload',
         'name'        : 'Download',
         'action'      : 'listDownloadForm',
         'permissions' : (CMFCorePermissions.View, ),
         'category'    : 'object',
         },
               )

    def searchMatchingReferences(self, searchterm):
        """ list existing references but rejects those already referenced
        """
        catalog = getToolByName(self, 'portal_catalog')
        field = self.getField('references_list')
        value = getattr(self, field.edit_accessor)()
        refList = [r for r
                   in catalog(SearchableText=searchterm, portal_type=search_types)
                   if r.getObject().UID() not in value]
        return refList
    
    def vocabCustomStyle(self):
        """ build a DisplayList based on existing styles
        """
        bltool = getToolByName(self, 'portal_bibliolist')
        return DisplayList(bltool.findBibrefStyles())

registerType(BibliographyList)