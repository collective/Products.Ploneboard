##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

""" BibrefCustomStyle:
    Presentation format to convert a bibliographic references list
    in a html format ready for publishing
"""
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField, LinesField
from Products.Archetypes.public import BooleanField, BooleanWidget
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, EpozWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget

from BibrefStyle import IBibrefStyle

from Products.ATBiblioList.config import *
#from Products.ATBiblioList.dummy_refs import dummy_refs

try:
    import roman
    HASDOCUTILS = 1
except ImportError:
    HASDOCUTILS = None

schema = BaseSchema + Schema((
    TextField('refDisplay',
              searchable=0,
              required=1,
              primary = 1,
              vocabulary=FORMAT_GENERICSTRING_STYLES,
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              default = DEFAULT_REFS_DISPLAY,
              allowable_content_types = ( 'text/html',),
              widget=EpozWidget(label='Format',
                          label_refpresentation_msgid="label_refpresentation_formatandorder",
                          description_msgid="help_refpresentation_formatandorder",
                          description=' Give the desired format of the bibliographic reference. Place a field using the following way: &#013; Author: %A &#013; Title: %T &#013; Publication_month: %m &#013; Publication_year: %y &#013; Journal: %J &#013; Institution: %I &#013; Organisation: %O &#013; Booktitle: %B &#013; Pages: %p &#013; Volume: %v &#013; Number: %n &#013; Editor(s): %E &#013; EditorFlag: %F &#013; Publisher: %P &#013; Adress: %a &#013; Pmid: %i &#013; Edition: %e &#013; Howpublished: %h &#013; Chapter: %c &#013; School: %S &#013; Preprint sever: %r &#013; Series: %s &#013; "%" sign: %%',
                          i18n_domain="plone")
              ),
    StringField('nameOrder',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_AUTHORS_LIST_ORDER,
                default='first middle last',
                widget=SelectionWidget(format='select',
                           label='Names Order',
                           description='Order the family name, 1st name, middlename the way you want.',
                           label_refpresentation_msgid="label_refpresentation_nameorderformat",
                           description_msgid="help_refpresentation_nameorderformat",
                           i18n_domain="plone",),
                ),
    StringField('firstnameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='First name author (in %A)',
                          description='Choose a fitting format for the first name.',
                          label_refpresentation_msgid="label_refpresentation_firstnameformat",
                          description_msgid="help_refpresentation_firstnameformat",
                          i18n_domain="plone"),
                ),
    StringField('middlenameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Middle name author (in %A)',
                          label_refpresentation_msgid="label_refpresentation_middlenameFormat",
                          description_msgid="help_refpresentation_middlenameFormat",
                          description='Choose a fitting format for the middle name.',
                          i18n_domain="plone"),
                ),
    StringField('lastnameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Family name author (in %A)',
                          label_refpresentation_msgid="label_refpresentation_lastnameformat",
                          description_msgid="help_refpresentation_lastNameFormat",
                          description='Choose a fitting format for the family name.',
                          i18n_domain="plone"),
                ),
    StringField('authorSeparator',
                searchable=0, 
                default=", ",
                widget=StringWidget(label='Default symbol or string between authors',
                          label_refpresentation_msgid='label_refpresentation_authorseparator',
                          description_msgid='help_refpresentation_nameseparatorformat',
                          description="Type the separator to put between each author, except between the two last authors(spaces included)",
                          i18n_domain="plone"),
                ),
    StringField('lastauthorSeparator',
                searchable=0, 
                default=", ",
                widget=StringWidget(label='Symbol or string between last author and its predecessor',
                          label_refpresentation_msgid='label_refpresentation_lastauthorseparator',
                          description_msgid='help_refpresentation_lastnameseparatorformat',
                          description="Type the separator to put between the two last authors(spaces included)",
                          i18n_domain="plone"),
                ),
    BooleanField('withAuthorUrl',
                 default=0,
                 widget=BooleanWidget(label='Authors with URL',
                          label_refpresentation_msgid='label_refpresentation_authorswithurl',
                          description_msgid='help_refpresentation_authorswithurl',
                          description="Check if authors link to their URL (if URL exists).",
                          i18n_domain="plone"),
                 ),
    StringField('titleFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_TITLE_STYLES,
                widget=SelectionWidget(format='select',
                          label='PublicationTitle (%T)',
                          label_refpresentation_msgid="label_refpresentation_titleformat",
                          description_msgid="help_refpresentation_titleformat",
                          description='Choose a fitting format for the title.',
                          i18n_domain="plone"),
               ),
    BooleanField('withTitleUrl',
                 default=0,
                 widget=BooleanWidget(label='Title with URL',
                          label_refpresentation_msgid='label_refpresentation_titleurl',
                          description_msgid='help_refpresentation__titleurl',
                          description="Check if authors link to their URL (if URL exists).",
                          i18n_domain="plone"),
                 ),

    StringField('journalFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Journal (%J)',
                          label_refpresentation_msgid="label_refpresentation_journalformat",
                          description_msgid="help_refpresentation_journalformat",
                          description='Choose a format on how to present the Journal name.',
                          i18n_domain="plone"),
                ),))
if HASDOCUTILS:
    schema = schema + Schema((
    StringField('pagesFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERSLISTS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Pages (%p)',
                          label_refpresentation_msgid="label_refpresentation_pagesformat",
                          description_msgid="help_refpresentation_pagesformat",
                          description='Choose a format on how to represent page numbers.',
                          i18n_domain="plone"),
                ),
    StringField('volumeFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Volume number(%v)',
                          label_refpresentation_msgid="label_refpresentation_volumeformat",
                          description_msgid="help_refpresentation_volumeformat",
                          description='Choose a format on how to present the volume number.',
                          i18n_domain="plone"),
                ),
    StringField('editionFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Edition number(%e)',
                          label_refpresentation_msgid="label_refpresentation_editionformat",
                          description_msgid="help_refpresentation_editionformat",
                          description='Choose a format on how to present the edition number.',
                          i18n_domain="plone"),
                ),
    StringField('chapterFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Chapter number(%c)',
                          label_refpresentation_msgid="label_refpresentation_chapterformat",
                          description_msgid="help_refpresentation_chapterformat",
                          description='Choose a format on how to present the chapter number.',
                          i18n_domain="plone"),
                ),
    StringField('numberFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Magazine/Journal/Report Number (%n)',
                          label_refpresentation_msgid="label_refpresentation_numberformat",
                          description='Choose a format on how to present the number.',
                          description_msgid="help_refpresentation_numberformat",
                          i18n_domain="plone"),
                ),))
schema = schema + Schema((
    StringField('seriesFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_TITLE_STYLES,
                widget=SelectionWidget(format='select',
                          label='Series Format (%s)',
                          label_refpresentation_msgid="label_refpresentation_seriesformat",
                          description='Choose a fitting format for the series name.',
                          description_msgid="help_refpresentation_seriesformat",
                          i18n_domain="plone"),
                ),
    StringField('bookTitleFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_TITLE_STYLES,
                widget=SelectionWidget(format='select',
                          label='Title of Book (for inbook reference) (%B)',
                          label_refpresentation_msgid="label_refpresentation_booktitleformat",
                          description='Choose a fitting format for the title of the book.',
                          description_msgid="help_refpresentation_booktitleformat",
                          i18n_domain="plone",)
                ),
    ))
        
class BibrefCustomStyle(BaseContent):
    """ object permitting to define a presentation format.
    """
    __implements__ = (IBibrefStyle ,)

    archetype_name = "Bibref Custom Style"

    global_allow = 0
    
    schema = schema

    actions = (
        {'id'          : 'view',
         'name'        : 'View',
         'action'      : 'string:${object_url}/bibrefcustomstyle_view',
         'permissions' : (CMFCorePermissions.View,)
         },
               )

    def formatDictionnary(self, refValues):
        """ formats a bibref dictionnary
        """

        formatstring = self.getRefDisplay()
        formatstring = formatstring.replace('%%', 'EsCaPe')

        # Authors
        authors = refValues.get('authors')
        new_authors = ''
        new_authors += self.formatAuthor(authors[0])
        if len(authors) > 1:
            if len(authors[1:-1]):
                for author in authors[1:-1]:
                    new_authors += '%s%s' % (self.authorSeparator,
                                             self.formatAuthor(author))
            new_authors += '%s%s' % (self.lastauthorSeparator,
                                     self.formatAuthor(authors[-1]))
        formatstring = formatstring.replace('%A', new_authors)

        # Other Fields
        replacedFields = (
            {'avatar': '%T', 'field': 'title', 'format': self.titleFormat, 'with_abs_url': self.withTitleUrl},
            {'avatar': '%m', 'field': 'publication_month'},
            {'avatar': '%y', 'field': 'publication_year'},
            {'avatar': '%J', 'field': 'journal', 'format': self.journalFormat},
            {'avatar': '%I', 'field': 'institution'},
            {'avatar': '%o', 'field': 'organization'},
            {'avatar': '%B', 'field': 'booktitle', 'format': self.bookTitleFormat},
            {'avatar': '%p', 'field': 'pages', 'format': self.pagesFormat},
            {'avatar': '%v', 'field': 'volume', 'format': self.volumeFormat},
            {'avatar': '%n', 'field': 'number', 'format': self.numberFormat},
            {'avatar': '%E', 'field': 'editor',},
            {'avatar': '%P', 'field': 'publisher',},
            {'avatar': '%e', 'field': 'edition', 'format': self.editionFormat},
            {'avatar': '%h', 'field': 'howpublished',},
            {'avatar': '%c', 'field': 'chapter', 'format': self.chapterFormat},
            {'avatar': '%S', 'field': 'school',},
            {'avatar': '%s', 'field': 'series', 'format': self.seriesFormat},
            {'avatar': '%a', 'field': 'address'},
            {'avatar': '%i', 'field': 'pmid'},
            {'avatar': '%r', 'field': 'preprint_server'},
            {'avatar': '%t', 'field': 'type'},
                          )

        for replacedField in replacedFields:
            avatar = replacedField.get('avatar')
            format = replacedField.get('format')
            with_abs_url = replacedField.get('with_url')
            replacement = ''
            field_name = replacedField.get('field')
            value = refValues.get(field_name)
            if value:
                replacement = self.formatAttribute(value, format)
                if with_abs_url:
                    url = refValues.absolute_url()
                    replacement = '<a href="%s">%s</a>' %(url, replacement)
                formatstring = formatstring.replace(avatar,replacement)

        formatstring = formatstring.replace('EsCaPe', '%')
        return formatstring

    def formatAuthor(self, author):
        """ format single author """
        format=self.nameOrder
        names = (('first', 'firstname', self.firstnameFormat),
                 ('middle', 'middlename', self.middlenameFormat),
                 ('last', 'lastname', self.lastnameFormat))
        for name in names:
            new_name = self.formatAttribute(author.get(name[1]), name[2])
            format = format.replace(name[0], new_name)
        if self.withAuthorUrl == 1:
            url = author.get('homepage')
            if url:
                format = '<a href="%s">%s</a>' %(url, format)
        return format.replace('  ', ' ')

    def formatAttribute(self, stringvar=None, format=None):
        """ Transforms a string into a reformatted string """
        if not stringvar:
            return ''
        if not format:
           return stringvar

        if 'ini' in format:
            punct_cars = [' ','-','.',',',';',':','!','?',
                          '[',']','(',')','{','}','%','#']
            for car in punct_cars:
                stringvar = stringvar.replace(car, 'STRINGSEPARATOR')
            initials = []
            for val in stringvar.split('STRINGSEPARATOR'):
                if len(val)and val not in punct_cars:
                    initials.append(val[0])
            if 'dot' in format:
                new_initials = []
                for initial in initials:
                    new_initials.append(initial+'.')
                initials = new_initials
            if 'space' in format:
                new_initials = []
                for initial in initials:
                    new_initials.append(initial+' ')
                initials = new_initials
            stringvar = ''.join(initials)

        if 'roman' in format and stringvar.isdigit() and HASDOCUTILS:
           stringvar = roman.toRoman(int(stringvar))

        if 'upper' in format: stringvar = stringvar.upper()
        if 'lower' in format: stringvar = stringvar.lower()

        #not yet implemented...
        if format == '1; 3; 5-8; 10+' in format:
           pass

        return stringvar.strip()

    def formatDummyList(self):
        """ renders a formatted bibref dummy list
            only used for display in custom style view
        """
        bltool = getToolByName(self, 'portal_bibliolist')
        formatted_list = []
        for ref in self.dummy_refs():
            style = self.UID()
            result = bltool.formatDicoRef(ref, style)
            formatted_list.append({'type':ref.get('ref_type')+' Reference', 'result':result})
        return formatted_list


registerType(BibrefCustomStyle)
