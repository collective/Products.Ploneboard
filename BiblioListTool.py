"""BiblioListTool main class"""

# Zope stuff
from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

# CMF stuff
#from Products.CMFCore.Expression import Expression
#from Products.CMFCore.ActionInformation import ActionInformation
#from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from BiblioListFormatter import IBiblioListFormatter
from formatters import MinimalFormat
import Products

class BiblioListTool(UniqueObject, Folder):
    """ Tool for managing format rendering for references 
        contained in the biblio list.
    """
    __implements__ = (IBiblioListFormatter, )

    id = 'portal_bibliolist'
    meta_type = 'BiblioList Tool'


    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    manage_options = (
        (Folder.manage_options[0],)
        + Folder.manage_options[2:]
        )

    index_html = None

    def __init__(self):
        self._setObject('Minimal', MinimalFormat('Minimal', ''))

    def all_meta_types(self):
        return filter(lambda x: IBiblioListFormatter \
                      in x.get('interfaces', []),
                      Products.meta_types)

    security.declarePublic('getRefFormatterNames')
    def getRefFormatterNames(self):
        """ returns a list with the names of the 
            available ref formatters
        """
        return [refFormatter.getFormatName()
                for refFormatter in self.objectValues()]

    def formatList(self, uids, format):
        """ renders a BibliographyList referenced objects
            in the specified format
        """
        refFormatter = self.getFormatter(format)

        if refFormatter:
            at_tool = getToolByName(self, 'archetype_tool')
            objs = [at_tool.lookupObject(uid) for uid in uids]
            return refFormatter.formatList(objs)

        return ('The Selected Formatter could not be found.',)

    def getFormatter(self, format):
        """ returns the formatter for the specified format
        """
        if format[0:4] == 'fmt_':
            for refFormatter in self.objectValues():
                if format[4:].lower() == refFormatter.getId().lower():
                    return refFormatter
        else:
            at_tool = getToolByName(self, 'archetype_tool')
            try:
                refFormatter = at_tool.lookupObject(format)
                return refFormatter
            except: return None

InitializeClass(BiblioListTool)
