##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" BibrefCustomStyleFolder class
"""

import string
from urllib import quote
from types import StringType

from DocumentTemplate import sequence

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseFolderSchema, Schema
from Products.Archetypes.public import BaseFolder, registerType

schema = BaseFolderSchema

def modify_fti(fti):
    """ overwrite the default immediate view """
    fti['immediate_view'] = 'folder_contents'

class BibrefCustomStyleFolder(BaseFolder):
    """ container for custom bibref styles
    """
    
    archetype_name = "Bibref Custom Style Folder"
    filter_content_types = 1
    allowed_content_types = ('BibrefCustomStyle', 'BibrefCustomStyleSet')

    schema = schema

registerType(BibrefCustomStyleFolder)

