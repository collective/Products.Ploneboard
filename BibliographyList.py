##########################################################################
#                                                                        #
#      written by: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" BibliographyList: personal list of bibliographic references
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ReferenceField, ReferenceField, StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget, SelectionWidget, ReferenceWidget
from Products.Archetypes.Registry import registerWidget
from roman import *

# possible types of bibliographic references by module 'CMFBibliography'
from Products.CMFBibliographyAT.config import REFERENCE_TYPES as search_types

class ReferencesWidget(TypesWidget):
    """ custom widget for TTW references input handling """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "references_widget",
        })

registerWidget(ReferencesWidget)

schema = BaseSchema + Schema((
    ReferenceField('references_list',
                   multiValued=1,
                   relationship='lists reference',
                   widget=ReferencesWidget(label="References",
                                           label_msgid="label_references_list",
                                           description_msgid="help_references_list",
                                           i18n_domain="plone",
                                           description="Select refenferces to put in your list",
                                           ),
                   ),
    StringField('PresentationFormat',
                multiValued=0,
                default = 'fmt_minimal',
                vocabulary="vocabPresFormat",
                enforce_vocabulary=1,
                widget=SelectionWidget(label="Presentation Format",
                              label_msgid="label_presentation",
                              description_msgid="help_presentation",
                              description="Select the format how you want to present your list",           
                              i18n_domain="plone",
                              format="select",),
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

    def tryPresentationFormat(self):
        """ test method to see if presentationformats exist and have been declared.
        """
        try:
            return self.getattr('PresentationFormat')
        except AttributeError:
            return None

    def searchMatchingReferences(self, searchterm):
        """ lists existing references but rejects those already referenced """

        catalog = getToolByName(self, 'portal_catalog')
        field = self.getField('references_list')
        value = getattr(self, field.edit_accessor)()
        refList = [r for r
                   in catalog(SearchableText=searchterm, portal_type=search_types)
                   if r.getObject().UID() not in value]
                
        return refList
    
    def vocabPresFormat(self):
        """ build a DisplayList based on existing formats """

        formatList = []
        bltool = getToolByName(self, 'portal_bibliolist')
        for refFormatter in bltool.objectValues():
            formatList.append(('fmt_'+refFormatter.getId().lower(),
                               refFormatter.title_or_id()))
        for refFormat in self.findCustomRefFormats():
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()+' (Custom Format)'))

        return DisplayList(tuple(formatList))

    def findCustomRefFormats(self):
        """ lists existing formats to select from """

        catalog = getToolByName(self, 'portal_catalog')
        formList = catalog(portal_type=('ReferencePresentation','ReferencePresentationSet'))
                
        return formList        

registerType(BibliographyList)