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
import roman

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField, LinesField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, EpozWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget

from Products.ATBiblioList.config import FORMAT_GENERICSTRING_STYLES, \
    FORMAT_MONTH_STYLES, FORMAT_YEAR_STYLES, FORMAT_NUMBERSLISTS_STYLES, \
    FORMAT_NUMBERS_STYLES, FORMAT_AUTHORS_LIST_ORDER

schema = BaseSchema + Schema((
    TextField('formatAndOrder',
              searchable=0,
              required=1,
              primary = 1,
              vocabulary=FORMAT_GENERICSTRING_STYLES,
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              default= 'Author: %A <br/> Title: %T <br/> Publication_month: %m <br/> Publication_year: %y <br/> Journal: %J <br/> Institution: %I <br/> Organisation: %O <br/> Booktitle: %B <br/> Pages: %p <br/> Volume: %v <br/> Number: %n <br/> Editor(s): %E <br/> EditorFlag: %F <br/> Publisher: %P <br/> Adress: %a <br/> Pmid: %i <br/> Edition: %e <br/> Howpublished: %h <br/> Chapter: %c <br/> School: %S <br/> Preprint sever: %r <br/> Series: %s <br/> "%" sign: %%',
              allowable_content_types = ( 'text/html',),
              widget=EpozWidget(label='Format',
                          label_msgid="label_formatandorder",
                          description_msgid="help_formatandorder",
                          description=' Give the desired format of the bibliographic reference. Place a field using the following way: &#013; Author: %A &#013; Title: %T &#013; Publication_month: %m &#013; Publication_year: %y &#013; Journal: %J &#013; Institution: %I &#013; Organisation: %O &#013; Booktitle: %B &#013; Pages: %p &#013; Volume: %v &#013; Number: %n &#013; Editor(s): %E &#013; EditorFlag: %F &#013; Publisher: %P &#013; Adress: %a &#013; Pmid: %i &#013; Edition: %e &#013; Howpublished: %h &#013; Chapter: %c &#013; School: %S &#013; Preprint sever: %r &#013; Series: %s &#013; "%" sign: %%',
                          i18n_domain="plone")
              ),
    StringField('nameOrderFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_AUTHORS_LIST_ORDER,
                widget=SelectionWidget(format='select',
                           label='Names Order',
                           description='Order the family name, 1st name, middlename the way you want.',
                           label_msgid="label_nameorderformat",
                           description_msgid="help_nameorderformat",
                           i18n_domain="plone",),
                ),
    StringField('firstnameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='First name author (in %A)',
                          description='Choose a fitting format for the first name.',
                          label_msgid="label_firstnameformat",
                          description_msgid="help_firstnameformat",
                          i18n_domain="plone"),
                ),
    StringField('middlenameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Middle name author (in %A)',
                          label_msgid="label_middlenameFormat",
                          description_msgid="help_middlenameFormat",
                          description='Choose a fitting format for the middle name.',
                          i18n_domain="plone"),
                ),
    StringField('lastNameFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Family name author (in %A)',
                          label_msgid="label_lastNameFormat",
                          description_msgid="help_lastNameFormat",
                          description='Choose a fitting format for the family name.',
                          i18n_domain="plone"),
                ),
    StringField('nameSeparatorFormat',
                searchable=0, 
                default=", ",
                widget=StringWidget(label='Default name separator',
                                    label_msgid='label_nameseparatorformat',
                                    description_msgid='help_nameseparatorformat',
                                    description="Type the separator to put between each author, except between the two last authors(spaces included)",
                                    i18n_domain="plone"),
                ),
    StringField('lastnameSeparatorFormat',
                searchable=0, 
                default=", ",
                widget=StringWidget(label='Last name separator',
                                    label_msgid='label_lastnameSeparatorFormat',
                                    description_msgid='help_lastnameSeparatorFormat',
                                    description="Type the separator to put between the two last authors(spaces included)",
                                    i18n_domain="plone"),
                ),
    StringField('titleFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='PublicationTitle (%T)',
                          label_msgid="label_titleformat",
                          description_msgid="help_titleformat",
                          description='Choose a fitting format for the title.',
                          i18n_domain="plone"),
               ),
    StringField('publicationYearFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_YEAR_STYLES,
                widget=SelectionWidget(format='select',
                          label='Publication year (%y)',
                          label_msgid="label_publicationyearformat",
                          description_msgid="help_publicationyearformat",
                          description='Choose a format on how to present years.',
                          i18n_domain="plone"),
                ),
    StringField('publicationMonthFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_MONTH_STYLES,
                widget=SelectionWidget(format='select',
                          label='Publication month (%m)',
                          label_msgid="label_publicationmonthformat",
                          description_msgid="help_publicationmonthformat",
                          description='Choose a format on how to present months.',
                          i18n_domain="plone"),
                ),
    StringField('journalFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Journal (%J)',
                          label_msgid="label_journalformat",
                          description_msgid="help_journalformat",
                          description='Choose a format on how to present the Journal name.',
                          i18n_domain="plone"),
                ),
    StringField('pagesFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERSLISTS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Pages (%p)',
                          label_msgid="label_pagesformat",
                          description_msgid="help_pagesformat",
                          description='Choose a format on how to represent page numbers.',
                          i18n_domain="plone"),
                ),
    StringField('volumeFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Volume number(%v)',
                          label_msgid="label_volumeformat",
                          description_msgid="help_volumeformat",
                          description='Choose a format on how to present the volume number.',
                          i18n_domain="plone"),
                ),
    StringField('editionFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Edition number(%e)',
                          label_msgid="label_editionformat",
                          description_msgid="help_editionformat",
                          description='Choose a format on how to present the edition number.',
                          i18n_domain="plone"),
                ),
    StringField('chapterFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Chapter number(%c)',
                          label_msgid="label_chapterformat",
                          description_msgid="help_chapterformat",
                          description='Choose a format on how to present the chapter number.',
                          i18n_domain="plone"),
                ),
    StringField('numberFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_NUMBERS_STYLES,
                widget=SelectionWidget(format='select',
                          label='Magazine/Journal/Report Number (%n)',
                          label_msgid="label_numberformat",
                          description='Choose a format on how to present the number.',
                          description_msgid="help_numberformat",
                          i18n_domain="plone"),
                ),
    StringField('seriesFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Series Format (%s)',
                          label_msgid="label_seriesformat",
                          description='Choose a fitting format for the series name.',
                          description_msgid="help_seriesformat",
                          i18n_domain="plone"),
                ),
    StringField('howPublishedFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Medium how it got published (%h)',
                          label_msgid="label_howpublishedformat",
                          description_msgid="help_howpublishedformat",
                          description='Choose a fitting format for this field.',
                          i18n_domain="plone"),
                ),
    StringField('editorFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Editor(s) (%E)',
                          label_msgid="label_editorformat",
                          description_msgid="help_editorformat",
                          description='Choose a fitting format for the editors names.',
                          i18n_domain="plone"),
                ),
    # StringField('editorFlagFormat',
    #           searchable=0, 
    #           multivalued=0,
    #           vocabulary=FORMAT_GENERICSTRING_STYLES,
    #           widget=SelectionWidget(format='select',
    #                      label='EditorFlag (%F)',
    #                      label_msgid="label_editorflagformat",
    #                      description_msgid="help_editorflagformat",
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
                          label_msgid="label_publisherformat",
                          description='Choose a fitting format for the publisher name.',
                          description_msgid="help_publisherformat",
                          i18n_domain="plone"),
                ),
    StringField('bookTitleFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Title of Book (for inbook reference) (%B)',
                          label_msgid="label_booktitleformat",
                          description='Choose a fitting format for the title of the book.',
                          description_msgid="help_booktitleformat",
                          i18n_domain="plone",)
                ),
    StringField('schoolFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='School publishing the proceeding (%S)',
                          label_msgid="label_schoolformat",
                          description='Choose a fitting format for the name of the school.',
                          description_msgid="help_schoolformat",
                          i18n_domain="plone",)
                ),
    StringField('organizationFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Organization publishing the proceeding (%O)',
                          label_msgid="label_organizationformat",
                          description='Choose a fitting format for the name of the organization.',
                          description_msgid="help_organizationformat",
                          i18n_domain="plone",)
                ),
    StringField('institutionFormat',
                searchable=0, 
                multivalued=0,
                vocabulary=FORMAT_GENERICSTRING_STYLES,
                widget=SelectionWidget(format='select',
                          label='Institution publishing the technical report (%I)',
                          label_msgid="label_institutionformat",
                          description='Choose a fitting format for the name of the institution.',
                          description_msgid="help_institutionformat",
                          i18n_domain="plone",)
                ),
    # StringField('typeFormat',
    #           searchable=0, 
    #           multivalued=0,
    #           vocabulary=FORMAT_GENERICSTRING_STYLES,
    #           widget=SelectionWidget(format='select',
    #                      label='Type of technical report (%t)',
    #                      label_msgid="label_typeformat",
    #                      description='Choose a fitting format for the field.',
    #                      description_msgid="help_typeformat",
    #                      i18n_domain="plone",)
    #           ),
    ))
        
class ReferencePresentation(BaseContent):
    """ object permitting to define a presentation format.
    """

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

        formatstring = self.getFormatAndOrder()
        formatstring = formatstring.replace('%%', '__%__')
        formatstring = formatstring.replace('%A', self.formatAuthors(entry))
        formatFields = {
             '%T': ('title', self.titleFormat),
             '%m': ('publication_month', self.publicationMonthFormat),
             '%y': ('publication_year', self.publicationYearFormat),
             '%J': ('journal', self.journalFormat),
             '%I': ('institution', self.institutionFormat),
             '%o': ('organization', self.organizationFormat),
             '%B': ('booktitle', self.bookTitleFormat),
             '%p': ('pages', self.pagesFormat),
             '%v': ('volume', self.volumeFormat),
             '%n': ('number', self.numberFormat),
             '%E': ('editor', self.editorFormat),
             '%P': ('publisher', self.publisherFormat),
             '%e': ('edition', self.editionFormat),
             '%h': ('howpublished', self.howPublishedFormat),
             '%c': ('chapter', self.chapterFormat),
             '%S': ('school', self.schoolFormat),
             '%s': ('series', self.seriesFormat)
                     }

        for fieldKey in formatFields.keys():
            field = entry.getField(formatFields[fieldKey][0])
            if field:
                value = getattr(entry, field.accessor)()
                if value:
                    try:
                        format = formatFields[fieldKey][1]
                        if format:
                            formatstring = formatstring.replace(fieldKey,
                                                                self.formatAttribute(value,
                                                                                     format))
                    except TypeError: formatstring = formatstring.replace(fieldKey,value)
                else:
                    formatstring = formatstring.replace(fieldKey,'')
            else:
                formatstring = formatstring.replace(fieldKey,'')

        noFormatFields = (('%a', 'address'),
                          ('%i', 'pmid'),
                          ('%r', 'preprint_server'))

        for fieldKey in noFormatFields:
            try:
                field = entry.getField(fieldKey[1])
                value = getattr(self, field.accessor)()
                formatstring = formatstring.replace(fieldKey[0],value)
            except AttributeError:
                pass

        if hasattr(entry,'type'): 
            #since each portal object has a type attribute, this 'try' is nescessary
            try:
                formatstring = formatstring.replace('%t',entry.getType())
            except AttributeError:
                pass

        formatstring = formatstring.replace('__%__', '%')

        return formatstring


    def formatAuthors(self, entry):
        """ authors rendered as a string separated by their respective 
            separators (generic and last)
        """
        authors = entry.getAuthorList()
        result = ''
        if authors == []:
            pass
        elif len(authors) == 1:
            result = self.formatAuthor(authors[0])
        else:
            result += '%s' % self.formatAuthor(authors[0])
            if len(authors[1:-1]):
                for author in authors[1:-1]:
                    result += '%s%s' % (self.nameSeparatorFormat,
                                        self.formatAuthor(author))
            result += '%s%s' % (self.lastnameSeparatorFormat,
                                self.formatAuthor(authors[-1]))
        return result

    def formatAuthor(self, author):
        """ format single author """
        result=''
        form=self.getNameOrderFormat()
        if form[0] == 'S':
            result += '%s%s' %(self.formatAttribute(author.get('lastname'),
                                                    self.lastNameFormat),' ')
        if form.count('John'):
            result += '%s%s' %(self.formatAttribute(author.get('firstname',),
                                                    self.firstnameFormat),' ')
        if form.count('Edward'):
            result += '%s%s' %(self.formatAttribute(author.get('middlename',),
                                                    self.middlenameFormat),' ')
        if form[-1] == 'h' and len(form)>5:
            result += '%s%s' %(self.formatAttribute(author.get('lastname',),
                                                    self.lastNameFormat),' ')
        return result.strip()
    

    def formatAttribute(self, stringvar=None, format=None):
        """ Transforms a string into a reformatted string """
        if not stringvar:
            return ''
        if not format:
           return stringvar

#        format = format.split('_')
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

        # I think this should be rewritten using a DateTime object
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

registerType(ReferencePresentation)