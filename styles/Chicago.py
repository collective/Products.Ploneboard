##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

""" ChicagoBibrefStyle Class
    Based on the Chicago Bibliography style as described here:
    http://www.dianahacker.com/resdoc/history/bibliography.html
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


class ChicagoBibrefStyle(BibrefStyle):
    """ specific formatter to process input in Chicago format
    """
    __implements__ = (IBibrefStyle,)

    meta_type = "Chicago Bibref Style"

    def __init__(self, id = 'Chicago', title = "Chicago bibliography reference style"):
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
                formatted_entry += '%s, ' % self.formatAuthor(authors[0])
            else:
                formatted_entry += '%s' % self.formatAuthor(authors[0])
                if len(authors[1:-1]):
                    for author in authors[1:-1]:
                        formatted_entry += ', %s' % self.formatAuthor(author)
                formatted_entry += ' and %s' % self.formatAuthor(authors[-1])
                formatted_entry += ', '

            # title
            if refValues.get('journal'):
                formatted_entry += '"%s" <i>%s</i>' % (refValues.get('title'),
                                                       refValues.get('journal'))
                if refValues.get('number'):
                    formatted_entry += ' no. %s,' % refValues.get('number')
                else: formatted_entry += ','
            elif refValues.get('bookTitle'):
                formatted_entry += '"%s" in <i>%s</i>.' % (refValues.get('title'),
                                                          refValues.get('bookTitle'))
            else:
                formatted_entry += '<i>%s</i>.' % refValues.get('title')

            # series
            if refValues.get('series'):
                formatted_entry += ' %s.' % refValues.get('series')

            # volume
            if refValues.get('volume'):
                formatted_entry += ' vol. %s,' % refValues.get('volume')

            # number
            if refValues.get('number') and entry_type != 'ArticleReference':
                formatted_entry += ' no. %s' % refValues.get('number')

            # edition
            if refValues.get('edition'):
                edition = refValues.get('edition')
                if edition.isdigit():
                    if edition != 1:
                        if edition[-1] == 1 and edition[-2] != 1:
                            formatted_entry += ' %ist ed.' % edition
                        elif edition[-1] == 3 and edition[-2] != 1:
                            formatted_entry += ' %ird ed.' % edition
                        else:
                            formatted_entry += ' %ith ed.' % edition
                else:
                    if edition not in ('first', u'première', 'eerste'):
                        formatted_entry += ' %s ed.' % edition

            # organization
            if refValues.get('organization'):
                formatted_entry += ' %s,' % refValues.get('organization')

            # school
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

            # howpublished
            if refValues.get('howpublished'):
                formatted_entry += ' %s,' % refValues.get('howpublished')

            # year
            pub_year = refValues.get('publication_year')
            if entry_type == 'ArticleReference':
                formatted_entry += ' (%s)' %pub_year
            else: formatted_entry += ' %s' %pub_year

            # pages
            if refValues.get('pages'):
                formatted_entry += ', %s.' % refValues.get('pages')
            else: formatted_entry += '.'

            # url
            url = refValues.get('publication_url')
            if url:
                formatted_entry += ' <a href="%s">%s</a>.' %(url, url)

        return formatted_entry

    def formatAuthor(self, author):
        """ formats a single author for this format """
        middle = author.get('middlename')
        if middle:
            result = '%s %s. %s' % (author.get('firstname'),
                                    middle[0],
                                    author.get('lastname'))
        else:
            result = '%s %s' % (author.get('firstname'),
                                author.get('lastname'))

        url = author.get('homepage')
        if url:
            result = '<a href="%s">%s</a>' %(url, result)
        return result

# Class instanciation
InitializeClass(ChicagoBibrefStyle)


def manage_addChicagoBibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('Chicago', ChicagoBibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
