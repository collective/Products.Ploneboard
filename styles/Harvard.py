##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
##########################################################################

""" HarvardBibrefStyle Class
    Based on the Harvard System Bibliography style as described here:
    http://www.ex.ac.uk/Affiliate/stloyes/harv.htm
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


class HarvardBibrefStyle(BibrefStyle):
    """ specific formatter to process input in Harvard format
    """
    __implements__ = (IBibrefStyle,)

    meta_type = "Harvard Bibref Style"

    def __init__(self, id = 'Harvard', title = "Harvard bibliography reference style"):
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

        if entry_type in REFERENCE_TYPES and entry_type != 'UnpublishedReference':

            # authors
            formatted_entry += self.formatauthors(refValues.get('authors'))

            # editorflag
            if refValues.get('editor_flag'):
                formatted_entry += ' (ed)'
            
            # year
            formatted_entry += ' ('
            if refValues.get('publication_year'):
                if refValues.get('publication_month'):
                    formatted_entry += '%s ' % refValues.get('publication_month')
                formatted_entry += '%s).' % refValues.get('publication_year')
            else:
                formatted_entry += 'n.d.).'

            # title
            formatted_entry += ' %s.' % refValues.get('title')

            # books 
            if entry_type == 'BookReference' or entry_type[:2] == 'In':
                # 'In'- reference 
                if entry_type[:2] == 'In':
                    formatted_entry += ' <u>In</u> %s,' % refValues.get('booktitle')
                # edition
                if refValues.get('edition'):
                    formatted_entry += ' %s ed.' % refValues.get('edition')
                # source
                if refValues.get('address'):
                    formatted_entry += ' %s,' % refValues.get('address')
                if refValues.get('publisher'):
                    formatted_entry += ' %s.' % refValues.get('publisher')
            
            # article
            elif entry_type == 'ArticleReference':
                # journal
                if refValues.get('journal'):
                    formatted_entry += ' %s,' % refValues.get('journal')                
                # volume
                if refValues.get('volume'):
                    formatted_entry += ' %s,' % refValues.get('volume')
                # pages
                if refValues.get('pages'):
                    formatted_entry += ' %s.' % refValues.get('pages')
            
            # thesis
            if refValues.get('school'):
                if refValues.get('type'):
                    formatted_entry += ' %s,' % refValues.get('type')
                formatted_entry += ' %s.' % refValues.get('school')

            # series
            if refValues.get('series'):
                formatted_entry += ' (%s no. %s)' % (refValues.get('series'), refValues.get('number'))
            
            # url
            url = refValues.get('publication_url')
            if url:
                formatted_entry += ' Retrieved from the World Wide Web: <a href="%s">%s</a>.' %(url, url)

        return formatted_entry
            
    def formatauthors(self, authors):
        formatted_entry = ''
        if authors == []:
            pass
        elif len(authors) == 1:
            formatted_entry += '%s ' % self.formatAuthor(authors[0])
        else:
            if len(authors[0:-1]):
                for author in authors[0:-1]:
                    formatted_entry += '%s, ' % self.formatAuthor(author)
            formatted_entry += 'and %s' % self.formatAuthor(authors[-1])
            formatted_entry += ' '
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
InitializeClass(HarvardBibrefStyle)


def manage_addHarvardBibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('Harvard', HarvardBibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
