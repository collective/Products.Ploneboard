##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
##########################################################################

""" APABibrefStyle Class
    Based on the APA (American Psychological Association) Bibliography style
    as described here:
    http://www.english.uiuc.edu/cws/wworkshop/bibliography_style_handbookapa.htm
    http://owl.english.purdue.edu/workshops/hypertext/apa/sources/reference.html
    http://www.westwords.com/guffey/apa.html
"""


# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.config import REFERENCE_TYPES

# Bibliolist stuff
from Products.ATBiblioList.BibrefStyle import IBibrefStyle, BibrefStyle


class APABibrefStyle(BibrefStyle):
    """ specific formatter to process input in APA format
    """
    __implements__ = (IBibrefStyle,)

    meta_type = "APA Bibref Style"

    def __init__(self, id = 'APA', title = "APA bibliography reference style"):
        """ initializes only id and title
        """
        self.id = id
        self.title = title

    def formatDictionnary(self, refValues):
        """ formats a bibref dictionnary
        """
        formatted_entry = ''

        entry_type = refValues.get('meta_type')
        if not entry_type:
            entry_type = refValues.get('ref_type')+'Reference'

        if entry_type in REFERENCE_TYPES:

            # authors
            authors = refValues.get('authors')
            if authors == []:
                pass
            elif len(authors) == 1:
                formatted_entry += '%s ' % self.formatAuthor(authors[0])
            else:
                if len(authors)<7:
                    for author in authors[0:-1]:
                        formatted_entry += '%s, ' % self.formatAuthor(author)
                    formatted_entry += '& %s' % self.formatAuthor(authors[-1])
                else:
                    for author in authors[0:7]:
                        formatted_entry += '%s, ' % self.formatAuthor(author)
                    formatted_entry += 'et al.' % self.formatAuthor(authors[-1])
                formatted_entry += ' '

            # year
            if entry_type == 'ArticleReference':
                formatted_entry += '(%s' % refValues.get('publication_year')
                if refValues.get('publication_month'):
                    formatted_entry += ', %s' % refValues.get('publication_month')
                formatted_entry += ').'
            else:
                formatted_entry += '(%s).' % refValues.get('publication_year')
            
            # title
            if entry_type == 'ArticleReference' or entry_type[:2] == 'In':
                formatted_entry += ' %s.' % refValues.get('title')
            else:
                formatted_entry += ' <i>%s</i>' % refValues.get('title')
    
            # 'In' part
            if entry_type[:2] == 'In':
                formatted_entry += ' In <i>%s</i>' % refValues.get('booktitle')

            # series
            if refValues.get('series'):
                formatted_entry += ', %s' % refValues.get('series')

            # Pages, Edition & Volume
            if refValues.get('volume') or refValues.get('edition') or (refValues.get('pages') and entry_type[:2] == 'In'):
                formatted_entry += ' ('
                if refValues.get('pages'):
                    formatted_entry += 'pp. %s ' % refValues.get('pages')
                if refValues.get('edition'):
                    formatted_entry += '%s ed. ' % refValues.get('volume')
                if refValues.get('volume'):
                    formatted_entry += 'vol. %s ' % refValues.get('volume')
                formatted_entry = formatted_entry.strip() + ')'
            formatted_entry += '.'

            # address & publisher
            if refValues.get('address'):
                formatted_entry += ' %s' % refValues.get('address')
                if  refValues.get('publisher'):
                    formatted_entry += ':'
                else:
                    formatted_entry += '.'
            if refValues.get('publisher'):
                formatted_entry += ' %s.' % refValues.get('publisher')

            # Journal & pages
            if refValues.get('journal'):
                formatted_entry += ' <i>%s</i>' % refValues.get('journal')
                if refValues.get('pages'):
                    formatted_entry += ' %s.' % refValues.get('pages')

            if formatted_entry.strip()[-1] == ',':
                formatted_entry = formatted_entry.strip()[:-1] + '.'

            # url
            url = refValues.get('publication_url')
            if url:
                formatted_entry += ' Retrieved from <a href="%s">%s</a>.' %(url, url)


        return formatted_entry

    def formatAuthor(self, author):
        """ formats a single author for this format """
        middle = author.get('middlename')
        if middle:
            result = '%s, %s. %s.' % (author.get('lastname'),
                                      author.get('firstname')[0],
                                      middle[0])
        else:
            result = '%s, %s.' % (author.get('lastname'),
                                  author.get('firstname')[0])
        url = author.get('homepage')
        if url:
            result = '<a href="%s">%s</a>' %(url, result)
        return result

# Class instanciation
InitializeClass(APABibrefStyle)


def manage_addAPABibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('APA', APABibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
