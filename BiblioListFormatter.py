"""BiblioListFormatter main class"""

# Zope stuff
from Interface import Interface
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
import Products


class IBiblioListFormatter(Interface):
    """ Interface for the format 
        renderers of the bibliolist tool.
    """
    def formatList(objs):
        """ returns the rendered list as a python list
            objs is the list of bibrefs objects referenced in the 
            BiblioList object
        """

class BiblioListFormatter(SimpleItem):
    """ Base class for the input formatter of the bibliolist tool.
    """
    __implements__ = (IBiblioListFormatter ,)

    meta_type = 'BiblioList Formatter'
    
    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        """ minimal initialization
        """
        self.id = id
        self.title = title
        self.format = format

    def formatList(self, objs):
        """ renders a formatted bibliography references list
        """
        formatted_list = []
        for obj in objs:
            formatted_list.append(self.formatEntry(obj))
        return formatted_list

    def formatEntry(self, entry):
        """ renders a formatted bibliography reference
        """
        pass # needs to be overwritten by individual formatters

# Class instanciation
InitializeClass(BiblioListFormatter)