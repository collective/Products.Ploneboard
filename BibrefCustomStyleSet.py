##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" BibrefCustomStyleSet: combining multiple BibrefCustomStyles to allow 
    each type of reference to have its own presentation format.
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import SelectionWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from BibrefStyle import IBibrefStyle

schema = BaseSchema + Schema((
    StringField('DefaultStyle',
#                 multiValued=0,
                 vocabulary="vocabCustomStyleSel",
                 relationship='has CustomStyleSel',
                 default='stl_minimal',
#                 enforce_vocabulary=1,
                 widget=SelectionWidget(label="Default Presentation Style",
                                        label_msgid="label_styleset_default",
                                        description_msgid="help_styleset_default",
                                        description="Select the default bibliographic style you want to present your list with.",
                                        i18n_domain="plone",
                                        format="select",
                                        ),
                   ),
                              ))

def buildStyleSetSchema():
    """ Dynamic schema building
    """
    
    presentation_set_schema = []
    for reftype in REFERENCE_TYPES:
        reftype = reftype.replace('Reference', ' Reference')+' Style'
        elem = StringField(reftype,
                           vocabulary = "vocabCustomStyleDef",
                           default = 'Default',
                           widget = SelectionWidget(label=reftype.replace('Reference Style', 'Reference'),
                                                    label_msgid="",
                                                    description_msgid="help_styleset_list",
                                                    description="Select the bibliographic style how you want to present your list for this type of reference.",
                                                    i18n_domain="plone",
                                                    format='pulldown',
                                                    ),
                           )
        presentation_set_schema.append(elem)

    return Schema(presentation_set_schema) 
    
class BibrefCustomStyleSet(BaseContent):
    """ Class combining multiple BibrefCustomStyles 
    """
    __implements__ = (IBibrefStyle ,)

    archetype_name = "Bibref Custom Style Set"

    global_allow = 0
    
    schema = schema + buildStyleSetSchema()

    actions = (
        {'id'          : 'view',
         'name'        : 'View',
         'action'      : 'string:${object_url}/bibrefcustomstyle_view',
         'permissions' : (CMFCorePermissions.View,)
         },
               )

    def vocabCustomStyleSel(self):
        """ values for the default bibref style """
        return self.buildVocab()

    def vocabCustomStyleDef(self):
        """ values for each specific bibtex type's style """
        return self.buildVocab(('Default','Default'))

    def buildVocab(self, default_value=None):
        """ build a DisplayList based on existing styles """
        if default_value:
            vocab = [default_value,]
        else:
            vocab = []
        bltool = getToolByName(self, 'portal_bibliolist')
        styles = bltool.findBibrefStyles()
        for style in styles:
            vocab.append(style)
        return DisplayList(tuple(vocab))

    def formatList(self, objs):
        """ render a formatted bibliography references list
        """
        formatted_list = []
        bltool = getToolByName(self, 'portal_bibliolist')
        for obj in objs:
            uid = (obj.UID(),)
            format = getattr(self, obj.meta_type.replace('Reference', ' Reference') + ' Style')
            formatted_list.append(bltool.formatList(uid, format)[0])
        return formatted_list

    def formatDummyList(self):
        """ renders a formatted bibref dummy list
            only used for display in custom style view
        """
        bltool = getToolByName(self, 'portal_bibliolist')
        default_style = self.getDefaultStyle()
        formatted_list = []
        for ref in self.dummy_refs():
            ref_type = ref['ref_type']
            field = self.getField(ref_type+' Reference Style')
            style = getattr(self, field.accessor)()
            if style.lower() == 'default':
                style = default_style
            result = bltool.formatDicoRef(ref, style)
            formatted_list.append({'type':ref_type+' Reference', 'result':result})
        return formatted_list

registerType(BibrefCustomStyleSet)