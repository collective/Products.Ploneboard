##########################################################################
#                                                                        #
#      written by: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" ReferencePresentation:
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

from BiblioListFormatter import IBiblioListFormatter

from Products.ATBiblioList.config import *
#from Products.ATBiblioList.dummy_refs import dummy_refs

try:
    import roman
    HAVEDOCUTILS = 1
except ImportError:
    HAVEDOCUTILS = None

schema = BaseSchema + Schema((
    TextField('refDisplay',
              searchable=0,
              required=1,
              primary = 1,
              vocabulary=FORMAT_GENERICSTRING_STYLES,
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              default= DEFAULT_REFS_DISPLAY,
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
                vocabulary=FORMAT_GENERICSTRING_STYLES,
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
    StringField('publicationYearFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_YEAR_STYLES,
                widget=SelectionWidget(format='select',
                          label='Publication year (%y)',
                          label_refpresentation_msgid="label_refpresentation_publicationyearformat",
                          description_msgid="help_refpresentation_publicationyearformat",
                          description='Choose a format on how to present years.',
                          i18n_domain="plone"),
                ),
    StringField('publicationMonthFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_MONTH_STYLES,
                widget=SelectionWidget(format='select',
                          label='Publication month (%m)',
                          label_refpresentation_msgid="label_refpresentation_publicationmonthformat",
                          description_msgid="help_refpresentation_publicationmonthformat",
                          description='Choose a format on how to present months.',
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
if HAVEDOCUTILS:
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
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Series Format (%s)',
                          label_refpresentation_msgid="label_refpresentation_seriesformat",
                          description='Choose a fitting format for the series name.',
                          description_msgid="help_refpresentation_seriesformat",
                          i18n_domain="plone"),
                ),
    StringField('howPublishedFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Medium how it got published (%h)',
                          label_refpresentation_msgid="label_refpresentation_howpublishedformat",
                          description_msgid="help_refpresentation_howpublishedformat",
                          description='Choose a fitting format for this field.',
                          i18n_domain="plone"),
                ),
    StringField('editorFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Editor(s) (%E)',
                          label_refpresentation_msgid="label_refpresentation_editorformat",
                          description_msgid="help_refpresentation_editorformat",
                          description='Choose a fitting format for the editors names.',
                          i18n_domain="plone"),
                ),
    # StringField('editorFlagFormat',
    #           searchable=0, 
    #           multivalued=0,
    #           vocabulary=FORMAT_GENERICSTRING_STYLES,
    #           widget=SelectionWidget(format='select',
    #                      label='EditorFlag (%F)',
    #                      label_refpresentation_msgid="label_refpresentation_editorflagformat",
    #                      description_msgid="help_refpresentation_editorflagformat",
    #                      description='Choose a fitting format for the editor flag.',
    #                      i18n_domain="plone"),
    #           ),
    # 
    StringField('publisherFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Publisher (%P)',
                          label_refpresentation_msgid="label_refpresentation_publisherformat",
                          description='Choose a fitting format for the publisher name.',
                          description_msgid="help_refpresentation_publisherformat",
                          i18n_domain="plone"),
                ),
    StringField('bookTitleFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Title of Book (for inbook reference) (%B)',
                          label_refpresentation_msgid="label_refpresentation_booktitleformat",
                          description='Choose a fitting format for the title of the book.',
                          description_msgid="help_refpresentation_booktitleformat",
                          i18n_domain="plone",)
                ),
    StringField('schoolFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='School publishing the proceeding (%S)',
                          label_refpresentation_msgid="label_refpresentation_schoolformat",
                          description='Choose a fitting format for the name of the school.',
                          description_msgid="help_refpresentation_schoolformat",
                          i18n_domain="plone",)
                ),
    StringField('organizationFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Organization publishing the proceeding (%O)',
                          label_refpresentation_msgid="label_refpresentation_organizationformat",
                          description='Choose a fitting format for the name of the organization.',
                          description_msgid="help_refpresentation_organizationformat",
                          i18n_domain="plone",)
                ),
    StringField('institutionFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Institution publishing the technical report (%I)',
                          label_refpresentation_msgid="label_refpresentation_institutionformat",
                          description='Choose a fitting format for the name of the institution.',
                          description_msgid="help_refpresentation_institutionformat",
                          i18n_domain="plone",)
                ),
    # StringField('typeFormat',
    #           searchable=0, 
    #           multivalued=0,
    #           vocabulary=FORMAT_GENERICSTRING_STYLES,
    #           widget=SelectionWidget(format='select',
    #                      label='Type of technical report (%t)',
    #                      label_refpresentation_msgid="label_refpresentation_typeformat",
    #                      description='Choose a fitting format for the field.',
    #                      description_msgid="help_refpresentation_typeformat",
    #                      i18n_domain="plone",)
    #           ),
    ))
        
class ReferencePresentation(BaseContent):
    """ object permitting to define a presentation format.
    """
    __implements__ = (IBiblioListFormatter ,)

    archetype_name = "Bibliography presentation format"

    global_allow = 0
    
    schema = schema

    def formatList(self, objs):
        """ renders a formatted bibliography references list
        """
        formatted_list = []
        for obj in objs:
            formatted_list.append(self.formatEntry(obj))
        return formatted_list

    def formatEntry(self, entry):
        """ renders a formatted bibliography reference """

        formatstring = self.getRefDisplay()
        formatstring = formatstring.replace('%%', 'EsCaPe')

        # Authors
        authors = entry.getAuthorList()
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
            {'avatar': '%T', 'field': 'title', 'format': self.titleFormat, 'with_url': self.withTitleUrl},
            {'avatar': '%m', 'field': 'publication_month', 'format': self.publicationMonthFormat},
            {'avatar': '%y', 'field': 'publication_year', 'format': self.publicationYearFormat},
            {'avatar': '%J', 'field': 'journal', 'format': self.journalFormat},
            {'avatar': '%I', 'field': 'institution', 'format': self.institutionFormat},
            {'avatar': '%o', 'field': 'organization', 'format': self.organizationFormat},
            {'avatar': '%B', 'field': 'booktitle', 'format': self.bookTitleFormat},
            {'avatar': '%p', 'field': 'pages', 'format': self.pagesFormat},
            {'avatar': '%v', 'field': 'volume', 'format': self.volumeFormat},
            {'avatar': '%n', 'field': 'number', 'format': self.numberFormat},
            {'avatar': '%E', 'field': 'editor', 'format': self.editorFormat},
            {'avatar': '%P', 'field': 'publisher', 'format': self.publisherFormat},
            {'avatar': '%e', 'field': 'edition', 'format': self.editionFormat},
            {'avatar': '%h', 'field': 'howpublished', 'format': self.howPublishedFormat},
            {'avatar': '%c', 'field': 'chapter', 'format': self.chapterFormat},
            {'avatar': '%S', 'field': 'school', 'format': self.schoolFormat},
            {'avatar': '%s', 'field': 'series', 'format': self.seriesFormat},
            {'avatar': '%a', 'field': 'address'},
            {'avatar': '%i', 'field': 'pmid'},
            {'avatar': '%r', 'field': 'preprint_server'},
            {'avatar': '%t', 'field': 'type'},
                          )

        for replacedField in replacedFields:
            avatar = replacedField.get('avatar')
            format = replacedField.get('format', None)
            with_url = replacedField.get('with_url', 0)
            replacement = ''
            field_name = replacedField.get('field')
            field = entry.getField(field_name)
            if field:
                value = getattr(entry, field.accessor)()
                if value:
                    replacement = self.formatAttribute(value, format)
                    if with_url:
                        url = entry.absolute_url()
                        replacement = '<a href="%s">%s</a>' %(url, replacement)
            formatstring = formatstring.replace(avatar,replacement)

        formatstring = formatstring.replace('%D', entry.Source())

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

        if 'roman' in format and stringvar.isdigit():
           stringvar = roman.toRoman(int(stringvar))

        if 'upper' in format:
           stringvar = stringvar.upper()
        if 'lower' in format:
           stringvar = stringvar.lower()

        # I think this should be rewritten using built-in python date formatting
        if 'm01' in format and stringvar.isdigit() and int(stringvar) < 10:
           # put month in a double digit format
           stringvar = "0" + stringvar
        if 'm1' in format and stringvar.isdigit():
           # put month in a single digit
           stringvar = string.atoi(stringvar)
        if 'yxx' in format:
            if len(stringvar) == 4:
                stringvar = stringvar[-2:]

        #not yet implemented...
        if format == '1; 3; 5-8; 10+' in format:
           pass

        return stringvar.strip()

    def formatDummyRefs(self):
        """ """
        return
        

registerType(ReferencePresentation)
