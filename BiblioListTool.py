##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

"""BiblioListTool class"""

# Zope stuff
from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

# CMF stuff
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

# ATBiblioList stuff
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

    security.declarePrivate('getBibrefStyleNames')
    def getBibrefStyleNames(self):
        """ returns a list with the names of the 
            available bibref styles
        """
        return [bibrefStyle.getFormatName()
                for bibrefStyle in self.objectValues()]

    security.declareProtected(CMFCorePermissions.View, 'formatList')
    def formatList(self, uids, style):
        """ renders BibliographyList referenced objects
            in the specified style
        """
        at_tool = getToolByName(self, 'archetype_tool')
        objs = [at_tool.lookupObject(uid) for uid in uids]
        return self.formatRefs(objs, style)

    security.declarePrivate('formatRefs')
    def formatRefs(self, objs, style):
        """ renders a formatted bibliography references list
        """
        uflist = [self.getEntryDict(obj) for obj in objs]
        formatted_list = [self.formatDicoRef(obj, style)
                          for obj in self.sortList(uflist)]
        return tuple(formatted_list)

    security.declarePrivate('sortList')
    def sortList(self, objs):
        """ sorts a list on lastname and publicationyear.
        """
        objs.sort(self.cmpYear)
        objs.sort(self.cmpLName)
        return objs

    security.declarePrivate('cmpLName')
    def cmpLName(self,obj_a,obj_b):
        """ compares 2 objects on their publication_year
        """
        authora=obj_a.get('authors')
        authorb=obj_b.get('authors')
        if authora != [] and authorb != []:
            return cmp(authora[0].get('lastname'),authorb[0].get('lastname'))
        else: 
            return -1

    security.declarePrivate('cmpYear')
    def cmpYear(self,obj_a,obj_b):
        """ compares 2 objects on their publication_year
        """
        return (obj_a.get('publication_year') > obj_a.get('publication_year'))

    security.declarePrivate('formatDicoRef')
    def formatDicoRef(self, refValues, style):
        """ returns a Bibliography Reference
            rendered in the specified style
            refValues must be a python dictionnary
        """
        bibrefStyle = self.getBibrefStyle(style)
        if bibrefStyle:
            return bibrefStyle.formatDictionnary(refValues)
        return 'The Selected Bibref Style could not be found.'

    security.declarePrivate('getBibrefStyle')
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

    security.declarePrivate('findBibrefStyles')
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
            if cstyle.meta_type == 'BibrefCustomStyle':
                styles.append((obj.UID(),obj.title_or_id()+' (Custom Style)'))
            if cstyle.meta_type == 'BibrefCustomStyleSet':
                styles.append((obj.UID(),obj.title_or_id()+' (Custom Style Set)'))
        return tuple(styles)

    security.declarePrivate('getEntryDict')
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
        tmp_title = unicode(entry.Title(),'utf-8')
        if tmp_title[-1] == '.': tmp_title = tmp_title[:-1]
        values['title'] = tmp_title
        uniauthors=[]
        for author in entry.getAuthorList():
            uniauthor={}
            for field in author.keys():
                uniauthor[field] = unicode(author.get(field),'utf-8')
            uniauthors.append(uniauthor)
        values['authors'] = uniauthors
        uniauthors=[]
        uniauthor={}
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
                try:
                    for x in range(value.len()):
                        value[x] = unicode(value[x],'utf-8')
                    values[attr] = value
                except:
                    values[attr] = unicode(value,'utf-8')
        values['source'] = unicode(entry.Source(),'utf-8')
        values['absolute_url'] = unicode(entry.absolute_url(),'utf-8')
        values['meta_type'] = unicode(entry.meta_type,'utf-8') 
        
        return values

InitializeClass(BiblioListTool)
