##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

"""BibrefStyle main class"""

# Zope stuff
from Interface import Interface
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
import Products


class IBibrefStyle(Interface):
    """ Interface for the format 
        renderers of the bibliolist tool.
    """
    def formatDictionnary(refValues):
        """ returns the rendered bib ref
            refValues must be a dictionnary holding all values
        """

class BibrefStyle(SimpleItem):
    """ Base class for the input formatter of the bibliolist tool.
    """
    __implements__ = (IBibrefStyle,)

    meta_type = 'Bibref Style'
    
    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        """ minimal initialization
        """
        self.id = id
        self.title = title

    def formatDictionnary(self, refValues):
        """ renders a formatted bibliography reference based on dictionnary values
        """
        pass # needs to be overwritten by individual styles


# Class instanciation
InitializeClass(BibrefStyle)