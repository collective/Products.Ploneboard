from Products.Archetypes.public import *
from Products.CompositePage.interfaces import IComposite
from Products.CompositePage.composite import Composite
from Products.CompositePack.config import PROJECTNAME, TOOL_ID
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

composite_schema = Schema((
                       StringField('layout', 
                                   widget=SelectionWidget(label='Layout',
                                                          format='select'),
                                  ) 
                    ))

class CMFCompositePage(BaseContent, Composite):
    """A basic, Archetypes-based Composite Page
    """
    __implements__ = BaseContent.__implements__ + (IComposite,)
    meta_type = portal_type = 'CMF Composite Page'
    archetype_name = 'Navigation Page'

    schema = BaseSchema + composite_schema

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'cp_view',
                'permissions': (CMFCorePermissions.View,)
               },)

    cp_view = Composite.__call__

    
    def getLayout(self):
      # refresh vocabulary
      composite_tool = getToolByName(self, TOOL_ID)
      #import pdb; pdb.set_trace()
      layouts = composite_tool.layouts.objectValues('CompositePack Viewlet')
      template_ids = [layout.getTemplate().getId() for layout in layouts]
      self.schema['layout'].vocabulary = template_ids
      # return the value of layouts
      print template_ids
      return self.layout
       
registerType(CMFCompositePage, PROJECTNAME)
