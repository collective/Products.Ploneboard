##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
#    project leader: David Convent, david.convent@naturalsciences.be     #
#       assisted by: Louis Wannijn, louis.wannijn@naturalsciences.be     #
#                                                                        #
##########################################################################

""" package installer for ATBiblioList """

from Products.CMFCore.CMFCorePermissions import AddPortalContent

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

PROJECTNAME = 'ATBiblioList'
GLOBALS = globals()
skin_names = ('bibliography_list',)

ADD_CONTENT_PERMISSION = AddPortalContent

registerDirectory('skins', GLOBALS)

def initialize(context):
    """ Import Types here to register them """
    import BibliographyList
    import BibrefCustomStyleFolder
    import BibrefCustomStyle
    import BibrefCustomStyleSet
    import BiblioListTool
    import styles

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    tools = ( BiblioListTool.BiblioListTool, )

    utils.ToolInit(
        'BiblioList Tool', tools=tools,
        product_name='ATBiblioList', icon='bib_tool.gif',
        ).initialize(context)

    styles.initialize(context)
