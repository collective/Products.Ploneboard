"""MinimalFormat class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.config import REFERENCE_TYPES

# Bibliolist stuff
from Products.ATBiblioList.BiblioListFormatter \
     import IBiblioListFormatter, BiblioListFormatter


class MinimalFormat(BiblioListFormatter):
    """ specific formatter to process input in minimal format
    """
    __implements__ = (IBiblioListFormatter,)

    meta_type = "Minimal Format"

    def __init__(self, id = 'Minimal',
                 title = "Minimal Format"):
        """ initializes only id and title
        """
        self.id = id
        self.title = title

    def formatEntry(self, entry):
        """ formats a BibliographyEntry object
        """
        formatted_entry = ''

        if entry.meta_type in REFERENCE_TYPES:
            #authors
            authors = entry.getAuthorList()
            if authors == []:
                pass
            elif len(authors) == 1:
                formatted_entry += '%s' % self.formatAuthor(authors[0])
            else:
                formatted_entry += '%s' % self.formatAuthor(authors[0])
                if len(authors[1:-1]):
                    for author in authors[1:-1]:
                        formatted_entry += ', %s' % self.formatAuthor(author)
                formatted_entry += ' and %s' % self.formatAuthor(authors[-1])
            # publication year
            formatted_entry += ' (%s):' % entry.getPublication_year()
            formatted_entry += ' <a href="%s">%s</a>.' % (entry.absolute_url(),
                                                          entry.Title())
            formatted_entry += ' - %s' % entry.Source()

        return formatted_entry

    def formatAuthor(self, author):
        """ """
        result = '%s %s %s' % (author.get('firstname'),
                               author.get('middlename'),
                               author.get('lastname'))
        url = author.get('homepage')
        if url:
            result = '<a href="%s">%s</a>' %(url, author)
        return result
    
# Class instanciation
InitializeClass(MinimalFormat)

   
def manage_addMinimalFormat(self, REQUEST=None):
    """ """
    try:
        self._setObject('Minimal', MinimalFormat())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The formatter you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
