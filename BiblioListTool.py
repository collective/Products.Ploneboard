##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

"""BiblioListTool class"""

# Zope stuff
from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

# CMF stuff
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from BibrefStyle import IBibrefStyle
from styles.Minimal import MinimalBibrefStyle
from styles.Chicago import ChicagoBibrefStyle
from styles.Harvard import HarvardBibrefStyle
from styles.MLA import MLABibrefStyle
from styles.APA import APABibrefStyle
import Products

class BiblioListTool(UniqueObject, Folder):
    """ Tool for managing format rendering for references 
        contained in the biblio list.
    """

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
        self._setObject('Minimal', MinimalBibrefStyle('Minimal', ''))
        self._setObject('Chicago', ChicagoBibrefStyle('Chicago', ''))
        self._setObject('Harvard', HarvardBibrefStyle('Harvard', ''))
        self._setObject('MLA', MLABibrefStyle('MLA', ''))
        self._setObject('APA', APABibrefStyle('APA', ''))

    def all_meta_types(self):
        return filter(lambda x: IBibrefStyle \
                      in x.get('interfaces', []),
                      Products.meta_types)

    security.declarePublic('getBibrefStyleNames')
    def getBibrefStyleNames(self):
        """ returns a list with the names of the 
            available bibref styles
        """
        return [bibrefStyle.getFormatName()
                for bibrefStyle in self.objectValues()]

    def formatList(self, uids, style):
        """ renders BibliographyList referenced objects
            in the specified style
        """
        at_tool = getToolByName(self, 'archetype_tool')
        objs = [at_tool.lookupObject(uid) for uid in uids]
        return self.formatRefs(objs, style)

    def formatRefs(self, objs, style):
        """ renders a formatted bibliography references list
        """
        formatted_list = []
        for obj in objs:
            refValues = self.getEntryDict(obj)
            formatted_list.append(self.formatDicoRef(refValues, style))
        return tuple(formatted_list)

    def formatDicoRef(self, refValues, style):
        """ renders a Bibliography reference dictionnary
            in the specified style
        """
        bibrefStyle = self.getBibrefStyle(style)
        if bibrefStyle:
            return bibrefStyle.formatDictionnary(refValues)
        return 'The Selected Bibref Style could not be found.'

    def getBibrefStyle(self, style):
        """ returns the formatter for the specified style
        """
        if style[:4] == 'stl_':
            for bibrefStyle in self.objectValues():
                if style[4:].lower() == bibrefStyle.getId().lower():
                    return bibrefStyle
        else:
            at_tool = getToolByName(self, 'archetype_tool')
            try:
                bibrefStyle = at_tool.lookupObject(style)
                return bibrefStyle
            except: return None

    def findBibrefStyles(self):
        """ used for building style selection vocabularies
        """
        styles = []
        # portal_bibliolist styles
        for style in self.objectValues():
            styles.append(('stl_'+style.getId().lower(),style.getId()))
        # custom styles and sets
        catalog = getToolByName(self, 'portal_catalog')
        cstyles = catalog(portal_type=('BibrefCustomStyle','BibrefCustomStyleSet'))
        for cstyle in cstyles:
            obj = cstyle.getObject()
            styles.append((obj.UID(),obj.title_or_id()+' (Custom Style)'))
        return tuple(styles)

    def getEntryDict(self, entry):
        """ 
        """
        ref_attributes = ('publication_year',
                          'publication_month',
                          'publication_url',
                          'abstract',
                          'note',
                          'publisher',
                          'editor',
                          'organization',
                          'institution',
                          'school',
                          'address',
                          'booktitle',
                          'chapter',
                          'journal',
                          'volume',
                          'edition',
                          'number',
                          'pages',
                          'series',
                          'type',
                          'howpublished',
                          'preprint_server',
                          'pmid',
                          'isbn',)

        values = {}
        tmp_title = entry.Title()
        if tmp_title[-1] == '.': tmp_title = tmp_title[:-1]
        values['title'] = tmp_title
        values['authors'] = entry.getAuthorList()
        for attr in ref_attributes:
            field = entry.getField(attr)
            if field:
                value = getattr(entry, field.accessor)()
                if not value:
                    try:
                        value = field.getDefault()
                    except TypeError:
                        # AT1.3 compliant
                        value = field.getDefault(entry)
                values[attr] = value
        values['source'] = entry.Source()
        values['absolute_url'] = entry.absolute_url()
        values['meta_type'] = entry.meta_type
        return values


InitializeClass(BiblioListTool)
