from Products.Archetypes.public import *
from Products.CompositePage.interfaces import IComposite
from Products.CompositePage.composite import Composite
from Products.CompositePack.config import PROJECTNAME
from Products.CMFCore import CMFCorePermissions

class CMFCompositePage(BaseContent, Composite):
    """A basic, Archetypes-based Composite Page
    """
    __implements__ = BaseContent.__implements__ + (IComposite,)
    meta_type = portal_type = 'CMF Composite Page'
    archetype_name = 'Navigation Page'

    schema = BaseSchema 

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'cp_view',
                'permissions': (CMFCorePermissions.View,)
               },)

    cp_view = Composite.__call__

registerType(CMFCompositePage, PROJECTNAME)
