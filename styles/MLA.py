##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
##########################################################################

""" MLABibrefStyle Class
    Based on the MLA (Modern Language Association) Bibliography style
    as described here:
    http://www.english.uiuc.edu/cws/wworkshop/MLA/bibliographymla.htm
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


class MLABibrefStyle(BibrefStyle):
    """ specific formatter to process input in MLA format
    """
    __implements__ = (IBibrefStyle,)

    meta_type = "MLA Bibref Style"

    def __init__(self, id='MLA', title="MLA bibliography reference style"):
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
                formatted_entry += '%s. ' % self.formatAuthor(authors[0])
            else:
                if len(authors[0:-1]):
                    for author in authors[0:-1]:
                        formatted_entry += '%s, ' % self.formatAuthor(author)
                formatted_entry += 'and %s' % self.formatAuthor(authors[-1])
                formatted_entry += '. '

            title = refValues.get('title')
            journal = refValues.get('journal')
            booktitle = refValues.get('booktitle')
            if journal:
                formatted_entry += '"%s." <i>%s.</i>.' % (title,journal)
            elif booktitle:
                formatted_entry += '"%s." <i>%s.</i>' % (title,booktitle)
            else:
                formatted_entry += '<i>%s.</i>' % (title)


            if entry_type == 'ArticleReference':
                # volume & number
                volume = refValues.get('volume')
                number = refValues.get('number')
                if volume:
                    formatted_entry += ' %s' % volume
                    if number:
                        formatted_entry += '.%s' % number
                else:
                    if number:
                        formatted_entry += ' %s' % number

                # year
                if refValues.get('publication_month'):
                    formatted_entry += ' (%s %s)' % (refValues.get('publication_month'),
                                                     refValues.get('publication_year'))
                else:
                    formatted_entry += ' (%s)' % refValues.get('publication_year')

                # pages
                if refValues.get('pages'):
                    formatted_entry += ': %s.' % refValues.get('pages')
                else:
                    formatted_entry += '.'


            else:
                # series, volume & edition
                if refValues.get('series'):
                    formatted_entry += ' %s.' % refValues.get('series')
                if refValues.get('volume'):
                    formatted_entry += ' vol. %s.' % refValues.get('volume')
                if refValues.get('edition'):
                    formatted_entry += ' %s ed.' % refValues.get('edition')

                # source
                if refValues.get('institution'):
                    formatted_entry += ' Diss. %s.' % refValues.get('institution')
                if refValues.get('organization'):
                    formatted_entry += ' %s,' % refValues.get('organization')
                if refValues.get('school'):
                    formatted_entry += ' %s,' % refValues.get('school')

                # address & publisher
                if refValues.get('address'):
                    formatted_entry += ' %s' % refValues.get('address')
                    if  refValues.get('publisher'):
                        formatted_entry += ':'
                    else:
                        formatted_entry += ','
                if refValues.get('publisher'):
                    formatted_entry += ' %s,' % refValues.get('publisher')

                # year
                formatted_entry += ' %s.' % refValues.get('publication_year')

                # pages
                if refValues.get('pages'):
                    formatted_entry += ' %s.' % refValues.get('pages')

            # url
            url = refValues.get('publication_url')
            if url:
                formatted_entry += ' <a href="%s">%s</a>' %(url, url)


        return formatted_entry

    def formatAuthor(self, author):
        """ formats a single author for this format """
        middle = author.get('middlename')
        if middle:
            result = '%s, %s %s' % (author.get('lastname'),
                                    author.get('firstname'),
                                    author.get('middlename'))
        else:
            result = '%s, %s' % (author.get('lastname'),
                                 author.get('firstname'))
        url = author.get('homepage')
        if url:
            result = '<a href="%s">%s</a>' %(url, result)
        return result

# Class instanciation
InitializeClass(MLABibrefStyle)


def manage_addMLABibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('MLA', MLABibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
