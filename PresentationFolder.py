##########################################################################
#                                                                        #
#   Project Leader: David Convent, david.convent@naturalsciences.be      #
#                                                                        #
#   written by: Louis Wannijn, louis.wannijn@naturalsciences.be          #
#                                                                        #
##########################################################################

""" BibliographyFolder main class """

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

class PresentationFolder(BaseFolder):
    """ container for presentation formats
    """
    
    archetype_name = "Presentation Folder"
    filter_content_types = 1
    allowed_content_types = ('ReferencePresentation' , 'RefPresentationSet' ,'ReferencePresentationSet' , 'Reference Presentation Set')

    schema = schema

registerType(PresentationFolder)

