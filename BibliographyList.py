##########################################################################
#                                                                        #
#   Project Leader: David Convent, david.convent@naturalsciences.be      #
#                                                                        #
#   written by: David Convent, david.convent@naturalsciences.be          #
#               Louis Wannijn, louis.wannijn@naturalsciences.be          #
#                                                                        #
##########################################################################

""" BibliographyList: personal list of bibliographic references
    Add-on to the CMFBibliographyAT Product
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ReferenceField, ReferenceField, StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import TypesWidget, SelectionWidget, ReferenceWidget

from roman import *

# possible types of bibliographic references by module 'CMFBibliography'
search_types = (
               'ArticleReference',
               'BookReference',
               'BookletReference',
               'InbookReference',
               'IncollectionReference',
               'InproceedingsReference',
               'MastersthesisReference',
               'ManualReference',
               'MiscReference',
               'PhdthesisReference',
               'PreprintReference',
               'ProceedingsReference',
               'TechreportReference',
               'UnpublishedReference',
               'WebpublishedReference',
               )

class ReferencesWidget(TypesWidget):
    """ custom widget for TTW references input handling """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "references_widget",
        })
try:
    from Products.Archetypes.Registry import registerWidget
    registerWidget(ReferencesWidget)
except ImportError:
    pass

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
    ReferenceField('PresentationFormat',
                   multiValued=0,
                   vocabulary="vocabPresFormat",
                   relationship='has PresFormat',
                   enforce_vocabulary=1,
                   widget=SelectionWidget(label="Presentation Format",
                              label_msgid="label_presentation",
                              description_msgid="help_presentation",
                              description="Select the format how you want to present your list",           
                              i18n_domain="plone",
                              format="select",
					                   ),
                   ),
    ))

class BibliographyList(BaseContent):
    """ Bibliography list class 
    """

    archetype_name = "Bibliography List"

    global_allow = 1
    
    schema = schema

    actions = (
        {'id'           : 'listdownload',
         'name'         : 'Download',
         'action'       : 'listDownloadForm',
         'permissions'  : (CMFCorePermissions.View, ),
         'category'     : 'object',
         },
               )

    def searchMatchingReferences(self, searchterm):
        """ lists existing references but rejects those already referenced """

        catalog = getToolByName(self, 'portal_catalog')
        refList = [r for r
                   in catalog(SearchableText=searchterm, portal_type=search_types)
                   if r.getObject().UID() not in self.getReferences_list()]
                
        return refList
    
    def vocabPresFormat(self):
        """ build a display list with available reference formats """

        formatList = []
        for refFormat in self.findRefFormats():
            obj = refFormat.getObject()
            formatList.append((obj.UID(),obj.title_or_id()))

        return DisplayList(tuple(formatList))

    def findRefFormats(self):
        """ lists existing formats to select from """

        catalog = getToolByName(self, 'portal_catalog')
        formList = catalog(portal_type=('ReferencePresentation','ReferencePresentationSet'))
                
        return formList  

    def reformatReference(self, item):
    
        presUID = self.getPresentationFormat()
 
        presentation = self.archetype_tool.lookupObject(uid = presUID) 
        if presentation.meta_type=='NoneType':
            return ''
        
        if presentation.meta_type=='ReferencePresentationSet':
            presUID = getattr(presentation, item.archetype_name +' Format')
            if presUID == 'Default':
                presUID = presentation.getDefaultFormat()
                if presUID == 'Select':
                    return ''
            presentation = self.archetype_tool.lookupObject(uid = presUID) 
        
        return self.apllyReformatReference(presentation, item)
    
    def apllyReformatReference(self, presentation, item):
        """ Put a reference of an item into a (html) formated string ready for publication """

        result= ''
        
        formatstring = presentation.getFormatAndOrder()
        
        code = 0
        for charac in formatstring:
            if code: 
                """If '%' was the previous character, the next character will be examined to insert a field value. 
                If the field can be formated the formatAttribute function will be called
                If the field does not exist for this reference, nothing will be inserted"""
                code = 0
                if charac=='A':
                    result=result + self.formatAuthors(item,presentation) # calls a separate function to compile the whole authorlist
                if charac=='T':
                    stringvar= self.formatAttribute(item.Title() or item.absolute_url(relative=1), presentation.getTitleFormat())
                    result=result + stringvar
                if charac=='m':
                    stringvar= self.formatAttribute(item.getPublication_month(), presentation.getPublicationMonthFormat())
                    result = result + stringvar
                if charac=='y':
                    stringvar= self.formatAttribute(item.getPublication_year(),  presentation.getPublicationYearFormat())
                    result = result + stringvar   
                if charac=='J':
                    if hasattr(item,'journal'):
                        stringvar= self.formatAttribute(item.getJournal(), presentation.getJournalFormat())
                        result = result + stringvar
                if charac=='I':
                    if hasattr(item,'institution'):
                        stringvar= self.formatAttribute(item.getInstitutio, ReferencePresentationSetn(), presentation.getInstitutionFormat())
                        result = result + stringvar
                if charac=='O':
                    if hasattr(item,'organization'):
                        stringvar= self.formatAttribute(item.getOrganization(), presentation.getOrganizationFormat())
                        result = result + stringvar
                if charac=='B':
                    if hasattr(item,'booktitle'):
                        stringvar= self.formatAttribute(item.getBooktitle(), presentation.getBookTitleFormat())
                        result = result + stringvar
                if charac=='p':
                    if hasattr(item,'pages'):
                        stringvar= self.formatAttribute(item.getPages(), presentation.getPagesFormat())
                        result = result + stringvar
                if charac=='v':
                    if hasattr(item,'volume'):
                        stringvar= self.formatAttribute(item.getVolume(), presentation.getVolumeFormat())
                        result = result + stringvar
                if charac=='n':
                    if hasattr(item,'number'):
                        stringvar= self.formatAttribute(item.getNumber(), presentation.getNumberFormat())
                        result = result + stringvar
                if charac=='t':
                    if hasattr(item,'type'): 
                        #since each archetype object has a type attribute, this 'try' is nescessary
                        try:
                            #stringvar= self.formatAttribute(item.getType(), presentation.getTypeFormat())
                            #result = result + stringvar
                            result = result + item.getType()
                        except AttributeError:
                            pass
                if charac=='E':
                    if hasattr(item,'editor'):
                        stringvar= self.formatAttribute(item.getEditor(), presentation.getEditorFormat())
                        result = result + stringvar
                """
                if charac=='F':
                    if hasattr(item,'editorFlag'):
                        stringvar= self.formatAttribute(item.getEditorFlag(), presentation.getEditorFlagFormat())
                        result = result + stringvar
                """
                if charac=='P':
                    if hasattr(item,'publisher'):
                        stringvar= self.formatAttribute(item.getPublisher(), presentation.getPublisherFormat())
                        result = result + stringvar
                if charac=='a':
                    if hasattr(item,'addres'):
                        result=result + item.getAddres()  
                if charac=='i':
                    if hasattr(item,'pmid'):
                        result=result + item.getPmid()  
                if charac=='e':
                    if hasattr(item,'edition'):
                        stringvar= self.formatAttribute(item.getEdition(), presentation.getEditionFormat())
                        result = result + stringvar
                if charac=='h':
                    if hasattr(item,'howpublished'):
                        stringvar= self.formatAttribute(item.getHowpublished(), presentation.getHowPublishedFormat())
                        result = result + stringvar
                if charac=='c':
                    if hasattr(item,'chapter'):
                        stringvar= self.formatAttribute(item.getChapter(), presentation.getChapterFormat())
                        result = result + stringvar
                if charac=='S':
                    if hasattr(item,'school'):
                        stringvar= self.formatAttribute(item.getSchool(), presentation.getSchoolFormat())
                        result = result + stringvar
                if charac=='r':
                    if hasattr(item,'preprint_server'):
                        result=result + item.getPreprint_server()
                if charac=='s':
                    if hasattr(item,'series'):
                        stringvar= self.formatAttribute(item.getSeries(), presentation.getSeriesFormat())
                        result = result + stringvar
                if charac=='%': #to show a % sign without having it erased for 'formatting' the next symbol, just double type the % sign
                    result=result + '%'  
            else:
                  #controls the character for fieldkeys to insert field values in the resulting string.
                  if charac == '%':
                      code = 1
                  else:
                      result=result + (charac)
        return result 

    def formatAuthors(self, item, presentation):
        """ putting the authors in a string spearated by their respective separators (generic and last) """

        authorList=item.getAuthorList()
        result = ''
        if len(authorList) > 2:
            for author in authorList[:-2]:
                result=result + self.formatAuthor(author, presentation) + presentation.getNameSeparatorFormat()
        if len(authorList) > 1:
            result=result + self.formatAuthor(authorList[-2], presentation) + ' ' + presentation.getLastNameSeparatorFormat() + self.formatAuthor(authorList[-1], presentation)
        else:
            result=self.formatAuthor(authorList[0], presentation)
        return result

    def formatAuthor(self, author, presentation):
        """ putting one author in a string, applying the seleceted formats (initials and such) and order (Familly name first or not...) """

        result=''
        form=presentation.getNameOrderFormat()
        if form[0]=='S':
            result=result+self.formatAttribute(author.get('lastname',''), presentation.getFamillyNameFormat())+' '
        if form.count('John'):
            result=result+self.formatAttribute(author.get('firstname',''), presentation.getFirstNameFormat())+' '
        if form.count('Edward'):
            result=result+self.formatAttribute(author.get('middlename',''), presentation.get2ndNameFormat())+' '
        if form[-1]=='h' and len(form)>5:
            result=result+self.formatAttribute(author.get('lastname',''), presentation.getFamillyNameFormat())+' '
        result=result[:-1]
        return result
    

    def formatAttribute(self, stringvar, format):
        """ Transforms a string into a reformatted string (initials, uppercase, roman numbers ect...) """

        if format == 'Format of the Field': #Unchanged
           return stringvar
        
        if format == 'FORMAT OF THE FIELD': #Uppercase
           return stringvar.upper()
        if format == 'format of the field': #Lowercase
           return stringvar.lower()
        if format == 'F.o.t.F.': #Initials separated by punctuation
           firstletter = '1' 
           newstring = ''
           for x in stringvar:
             if firstletter  and not (x in [' ','-','.',',',';',':']):
               newstring=newstring+x+"."
               firstletter = 0
             else:
               if x in [' ','-','.',',',';',':']:
                 firstletter =1
           return newstring
        if format == 'FotF': #Initials 
           firstletter  = 1 
           newstring = ''
           for x in stringvar:
             if firstletter and not (x in [' ','-','.',',',';',':']):
               newstring=newstring+x
               firstletter = 0
             else:
               if x in [' ','-','.',',',';',':']:
                 firstletter =1
           return newstring
        if format == 'F.O.T.F.': #Initials separated by punctuation uppercase
           stringvar = self.formatAttribute(stringvar, 'F.o.t.F.')
           return stringvar.upper()
        if format == 'FOTF': #Initials uppercase
           stringvar = self.formatAttribute(stringvar, 'FotF')
           return stringvar.upper()
        if format == 'f.o.t.f.': #Initials separated by punctuation lowercase
           stringvar = self.formatAttribute(stringvar, 'F.o.t.F.')
           return stringvar.lower()
        if format == 'fotf': #Initials lowercase
           stringvar = self.formatAttribute(stringvar, 'FotF')
           return stringvar.lower() 
        if format == 'm01': #puts months in a double digit format
           if stringvar < 10:
             return "0"+stringvar
           else:
             return stringvar
        #puts months in a single digit format when the month is before oktober
        if format == 'm1':
           return string.atoi(stringvar)
        if format == '19xx': #puts year in a 4digit format (or keeps it as it was entered that way => unchanged
           return stringvar
        if format == 'xx': #forces year in a 2 digit format (makes use of the 2digit month function)
           stringvar = (stringvar % 100)
           return self.formatAttribute(stringvar, 'm01')
        if format == '1, 3, 5-8, 10+': #not yet used... can be implemented by replacing the obliged separator by another one
           return stringvar
        if format == '1; 3; 5-8; 10+': #not yet used... can be implemented by replacing the obliged separator by another one
           return stringvar
        if format == 'digital: 12': #keeps the number in digital format
           return stringvar
        if format == 'Roman: XII': #transforms the number in a Roman numeric format (uppercase)
           return self.DecimalToRomanNumerals(stringvar)
        if format == 'Roman: xii': #transforms the number in a Roman numeric format (lowercase)
           stringvar = self.DecimalToRomanNumerals(stringvar)
           return stringvar.lower()
        
    def DecimalToRomanNumerals(self, base10_integer):
        """ this method converts an integer number in its Roman Numeral equivalent 
            Translated from a public domain C routine by Jim Walsh in the
            Snippets collection.
        """
        try:
            base10_integer=int(base10_integer)
            roman = ""
            n, base10_integer = divmod(base10_integer, 1000)
            roman = "M"*n
            if base10_integer >= 900:
                roman = roman + "CM"
                base10_integer = base10_integer - 900
            while base10_integer >= 500:
                roman = roman + "D"
                base10_integer = base10_integer - 500
            if base10_integer >= 400:
                roman = roman + "CD"
                base10_integer = base10_integer - 400
            while base10_integer >= 100:
                roman = roman + "C"
                base10_integer = base10_integer - 100
            if base10_integer >= 90:
                roman = roman + "XC"
                base10_integer = base10_integer - 90
            while base10_integer >= 50:
                roman = roman + "L"
                base10_integer = base10_integer - 50
            if base10_integer >= 40:
                roman = roman + "XL"
                base10_integer = base10_integer - 40
            while base10_integer >= 10:
                roman = roman + "X"
                base10_integer = base10_integer - 10
            if base10_integer >= 9:
                roman = roman + "IX"
                base10_integer = base10_integer - 9
            while base10_integer >= 5:
                roman = roman + "V"
                base10_integer = base10_integer - 5
            if base10_integer >= 4:
                roman = roman + "IV"
                base10_integer = base10_integer - 4
            while base10_integer > 0:
                roman = roman + "I"
                base10_integer = base10_integer - 1
            return roman
        except ValueError:
            return base10_integer

registerType(BibliographyList)
