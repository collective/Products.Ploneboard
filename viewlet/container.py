from Products.Archetypes.public import *
from Products.CompositePack.config import PROJECTNAME
from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import UniqueObject

class ViewletContainer(BaseFolderMixin, UniqueObject):
    """A basic, Archetypes-based Composite Element
    that uses references instead of path, and a dropdown
    for selecting templates
    """
    id = 'viewlets'
    meta_type = portal_type = archetype_name = 'CompositePack Viewlet Container'
    schema = MinimalSchema

    def all_meta_types(self):
        return BaseFolderMixin.all_meta_types(
            self, interfaces=(IViewlet,))

registerType(ViewletContainer, PROJECTNAME)
