##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

""" MinimalBibrefStyle class
    Default bibliography style
"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.config import REFERENCE_TYPES

# Bibliolist stuff
from Products.ATBiblioList.BibrefStyle \
     import IBibrefStyle, BibrefStyle


class MinimalBibrefStyle(BibrefStyle):
    """ specific formatter to process input in minimal format
    """
    __implements__ = (IBibrefStyle,)

    meta_type = "Minimal Bibref Style"

    def __init__(self, id = 'Minimal',
                 title = "Minimal bibliography reference style"):
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
            #authors
            authors = refValues.get('authors')
            if authors == []:
                pass
            elif len(authors) == 1:
                formatted_entry += '%s ' % self.formatAuthor(authors[0])
            else:
                formatted_entry += '%s' % self.formatAuthor(authors[0])
                if len(authors[1:-1]):
                    for author in authors[1:-1]:
                        formatted_entry += ', %s' % self.formatAuthor(author)
                formatted_entry += ' and %s' % self.formatAuthor(authors[-1])
                formatted_entry += ' '

            # publication year
            if refValues.get('publication_year'):
                formatted_entry += ' (%s):' % refValues.get('publication_year')

            # title
            absolute_url = refValues.get('absolute_url')
            title = refValues.get('title')
            if absolute_url:
                title = ' <a href="%s">%s</a>.' % (absolute_url, title)
            formatted_entry = formatted_entry + ' ' + title

            #source
            formatted_entry += ' - %s' % refValues.get('source')

        return formatted_entry

    def formatAuthor(self, author):
        """ """
        result = '%s %s %s' % (author.get('firstname'),
                               author.get('middlename'),
                               author.get('lastname'))
        url = author.get('homepage')
        if url:
            result = '<a href="%s">%s</a>' %(url, result)
        return result
    
# Class instanciation
InitializeClass(MinimalBibrefStyle)

   
def manage_addMinimalBibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('Minimal', MinimalBibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
