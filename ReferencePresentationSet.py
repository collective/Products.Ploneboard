##########################################################################
#                                                                        #
#      written by: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" ReferencePresentationSet: combining multiple referencepresentations to allow each type of reference to have its own presentation format.
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import SelectionWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES


schema = BaseSchema + Schema((
    StringField('DefaultFormat',
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
    """ Dynamic build of the schema
    """
    
    presentation_set_schema = []
    for reftype in REFERENCE_TYPES:
        reftype = reftype.replace('Reference', ' Reference')+' Format'
        elem = StringField(reftype,
                           vocabulary = "vocabPresFormatDef",
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
        return self.buildVocab(('Select', 'Select'))

    def vocabPresFormatDef(self):
        """ values for each specific reference format """
        return self.buildVocab(('Default','Default'))

    def buildVocab(self, default_value):
        """ build a DisplayList based on existing formats """
        formatList = [default_value,]
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
        formList = catalog(portal_type='ReferencePresentation')
                
        return formList        

    def formatList(self, objs):
        """ renders a formatted bibliography references list
        """
        formatted_list = []
        bltool = getToolByName(self, 'portal_bibliolist')
        for obj in objs:
            uid = (obj.UID(),)
            format = getattr(self, obj.meta_type.replace('Reference', ' Reference') + ' Format')
            formatted_list.append(bltool.formatList(uid, format)[0])
        return formatted_list


registerType(ReferencePresentationSet)