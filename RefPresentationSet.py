##########################################################################
#                                                                        #
#      written by: Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" ReferencePresentationSet: combining multiple referencepresentations to allow each type of reference to have its own presentation format.
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ReferenceField, ReferenceField, StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget, SelectionWidget, ReferenceWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES

# possible types of bibliographic references by module 'CMFBibliography'

schema = BaseSchema + Schema((
                              ReferenceField('DefaultFormat',
                                             multiValued=0,
                                             vocabulary="vocabPresFormat('Select')",
                                             relationship='has PresFormat',
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

class RefPresentationSet(BaseContent):
    """ Class combining multiple referencepresentations 
    """

    archetype_name = "Reference Presentation Set"

    global_allow = 0
    
    schema = schema + self.buildPresentationSetSchema()

    actions = (
        {'id'           : 'view',
         'name'         : 'View',
         'action'       : 'string:${object_url}/base_view',
         'permissions'  : (CMFCorePermissions.View,),
         'category'     : 'object',
         },
              ) 

    def buildPresentationSetSchema(self):
        """ Dynamically creates a shema using the existing bibliographic references (defined in CMFBibliographyAT) and the already userdefined presentationformats for references."""
        default_value = 'Default'
        
        formatList = self.vocabPresFormatDefault('Default')
        
        pres_set_schema = []
        for reftype in REFERENCE_TYPES:
            elem = StringField(reftype,
                               vocabulary = formatList,
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
    
    def vocabPresFormatDefault(self,DefaultValue):
        """ build a display list with available reference formats """

        formatList = [(DefaultValue,DefaultValue)]
        for refFormat in self.findRefFormats():
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()))

        return DisplayList(tuple(formatList))

registerType(RefPresentationSet)