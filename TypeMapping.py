"""
Maps Metadata Sets onto Content Types

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from ZopeImports import *
from Compatibility import getContentTypeNames, getToolByName
from Exceptions import ConfigurationError

DEFAULT_MAPPING_NAME = 'Default'

class TypeMappingContainer(Folder):

    meta_type = 'Type Mapping Container'

    manage_options = (

        {'label':'Content Types',
         'action':'manage_main'},

        {'label':'Metadata Tool',
         'action':'../manage_workspace'},
        )

    manage_main = DTMLFile('ui/TypeMappingContainerForm', globals())

    def __init__(self, id):
        self.id = id
        self.default_chain = ''

    def setDefaultChain(self, chain, RESPONSE=None):

        if not verifyChain(self, chain):
            raise ConfigurationError("invalid metadata set")

        self.default_chain = chain

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')

    def getDefaultChain(self):
        return self.default_chain

    def getChainFor(self, content_type):
        try:
            ctm = self._getOb(content_type)
        except AttributeError:
            return DEFAULT_MAPPING_NAME
        return ctm.getMetadataChain()

    def getMetadataSetsFor(self, content_type):
        try:
            ctm = self._getOb(content_type) # will throw attr error
        except AttributeError:
            return getMetadataSets(self, self.default_chain)
        return ctm.getMetadataSets()

    def getTypeMappings(self):
        return self.objectValues(TypeMapping.meta_type)

    def getTypeMappingFor(self, content_type):
        try:
            ctm = self._getOb(content_type)
        except AttributeError:
            return None
        return ctm

    def editMappings(self, default_chain, type_chains, RESPONSE=None):
        """ """
        self.setDefaultChain(default_chain)

        for tcr in type_chains:
            t = tcr['type']
            tc = tcr['chain']
            tc = tc.strip()
            if tc == DEFAULT_MAPPING_NAME:
                if self.getChainFor(t) != DEFAULT_MAPPING_NAME:
                    self._delObject(t)
            elif tc == self.getChainFor(t):
                continue
            else:
                tm = self.getTypeMappingFor(t)
                if tm is None:
                    self._setObject(t, TypeMapping(t))
                    ctm = self._getOb(t)
                    ctm.setMetadataChain(tc)
                else:
                    tm.setMetadataChain(tc)

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')

    def getContentTypes(self):
        return getContentTypeNames(self)

class TypeMapping(Folder):

    meta_type = 'Metadata Type Mapping'

    def __init__(self, id):
        self.id = id
        self.chain = None

    def getMetadataChain(self):
        return self.chain

    def setMetadataChain(self, chain):
        if not verifyChain(self, chain):
            raise ConfigurationError("invalid metadata set")
        self.chain = chain

    def getMetadataSets(self):
        return getMetadataSets(self, self.chain)

def getMetadataSets(ctx, chain):
    sets = filter(None, [c.strip() for c in chain.split(',')])
    tool = getToolByName(ctx, 'portal_metadata')
    return map(tool.getMetadataSet, sets)

def verifyChain(ctx, chain):
    try:
        getMetadataSets(ctx, chain)
    except AttributeError:
        return 0
    return 1
