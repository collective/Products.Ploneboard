##########################################################################
#                                                                        #
#   Project Leader: David Convent, david.convent@naturalsciences.be      #
#                                                                        #
#   written by: Louis Wannijn, louis.wannijn@naturalsciences.be          #
#                                                                        #
##########################################################################

""" ReferencePresentationSet: combining multiple referencepresentations to allow each type of reference to have its own presentation format.
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ReferenceField, StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget, SelectionWidget, ReferenceWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES

refTypesList = (
               'Article Reference',
               'Book Reference',
               'Booklet Reference',
               'Inbook Reference',
               'Incollection Reference',
               'Inproceedings Reference',
               'Mastersthesis Reference',
               'Manual Reference',
               'Misc Reference',
               'Phdthesis Reference',
               'Preprint Reference',
               'Proceedings Reference',
               'Techreport Reference',
               'Unpublished Reference',
               'Webpublished Reference',
               )


# possible types of bibliographic references by module 'CMFBibliography'

schema = BaseSchema + Schema((
                              ReferenceField('DefaultFormat',
                                             multiValued=0,
                                             vocabulary="vocabPresFormatSel",
                                             relationship='has PresFormatSel',
                                             enforce_vocabulary=1,
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
        """ Dynamically creates a shema using the existing bibliographic references (defined in CMFBibliographyAT) and the already userdefined presentationformats for references."""
        default_value = 'Default'
        
        pres_set_schema = []

#        portal = restricted
#        types_tool = getToolByName(self, 'portal_types')
#        refTypesList = []
#        refTypes = REFERENCE_TYPES
#        for refType in refTypes:
#            type_name = getattr(types_tool, refType, None).Title()
#            if not type_name:
#                raise TypeError, "%s not registered with the types tool." %type_name
#            else:
#                refTypesList.append(type_name)

        for reftype in refTypesList:
            elem = StringField(reftype+' Format',
                               vocabulary = "vocabPresFormatDef",
                               relationship='has PresFormatDef',
                               enforce_vocabulary = 1,
                               default = default_value,
                               widget = SelectionWidget(label = reftype,
                                                        description_msgid = "help_formatset",
                                                        description = "Select the format how you want to present your list for this type of reference.",
                                                        i18n_domaine = "plone",
                                                        format = 'pulldown',
                                                        ),
                               )
            pres_set_schema.append(elem)
        return Schema(pres_set_schema) 
    
class ReferencePresentationSet(BaseContent):
    """ Class combining multiple referencepresentations 
    """

    archetype_name = "Reference Presentation Set"

    global_allow = 0
    
    schema = schema + buildPresentationSetSchema()

    def vocabPresFormatSel(self):
        """ build a display list with available reference formats """

        formatList = [('Select','Select')]
        for refFormat in self.findRefFormats():
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()))

        return DisplayList(tuple(formatList))

    def vocabPresFormatDef(self):
        """ build a display list with available reference formats """

        formatList = [('Default','Default')]
        for refFormat in self.findRefFormats():
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()))

        return DisplayList(tuple(formatList))

    def findRefFormats(self):
        """ lists existing formats to select from """

        catalog = getToolByName(self, 'portal_catalog')
        formList = [r for r in catalog(portal_type='ReferencePresentation')]
                
        return formList  
registerType(ReferencePresentationSet)