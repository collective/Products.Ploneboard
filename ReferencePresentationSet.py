##########################################################################
#                                                                        #
#   Project Leader: David Convent, david.convent@naturalsciences.be      #
#                                                                        #
#   written by: David Convent, david.convent@naturalsciences.be          #
#               Louis Wannijn, louis.wannijn@naturalsciences.be          #
#                                                                        #
##########################################################################

""" ReferencePresentationSet:
    Combining multiple referencepresentations to allow each type
    of reference to have its own presentation format.
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ReferenceField, StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget, SelectionWidget, ReferenceWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES


schema = BaseSchema + Schema((
    StringField('DefaultFormat',
                multiValued=0,
                vocabulary="vocabPresFormatSel",
#                relationship='has PresFormatSel',
#                enforce_vocabulary=1,
                widget=SelectionWidget(label="Default Presentation Format",
                                       label_msgid="label_presentation",
                                       description_msgid="help_presentation",
                                       description="Select the format how you want to present your list",
                                       i18n_domain="plone",
                                       format="select",
                                       ),
                ),
                              ))

def buildPresentationSetSchema():
    """ Dynamic build of the schema
    """
    
    presentation_set_schema = []
    for reftype in REFERENCE_TYPES:
        reftype = reftype.replace('Reference', ' Reference')
        elem = StringField(reftype+' Format',
                           vocabulary = "vocabPresFormatDef",
#                           relationship='has PresFormatDef',
#                           enforce_vocabulary = 1,
                           default = 'Default',
                           widget = SelectionWidget(description_msgid = "help_formatset",
                                                    description = "Select the format how you want to present your list for this type of reference.",
                                                    i18n_domaine = "plone",
                                                    format = 'pulldown',
                                                    ),
                           )
        presentation_set_schema.append(elem)

    return Schema(presentation_set_schema) 
    
class ReferencePresentationSet(BaseContent):
    """ Class combining multiple referencepresentations 
    """

    archetype_name = "Reference Presentation Set"

    global_allow = 0
    
    schema = schema + buildPresentationSetSchema()

    def vocabPresFormatSel(self):
        """ values for the default reference format """
        return self.buildList(('Select', 'Select'))

    def vocabPresFormatDef(self):
        """ values for each specific reference format """
        return self.buildList(('Default','Default'))

    def buildList(self, default_value):
        """ lists existing formats to select from """

        formatList = [default_value,]
        catalog = getToolByName(self, 'portal_catalog')
        for refFormat in [r for r in catalog(portal_type='ReferencePresentation')]:
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()))

        return DisplayList(tuple(formatList))

registerType(ReferencePresentationSet)