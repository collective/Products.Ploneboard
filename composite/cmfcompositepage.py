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

class CMFCompositePage(BaseFolder, Composite):
    """A basic, Archetypes-based Composite Page
    """
    __implements__ = BaseFolder.__implements__ + (IComposite,)
    meta_type = portal_type = 'CMF Composite Page'
    archetype_name = 'Navigation Page'

    schema = BaseSchema + composite_schema

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'cp_view',
                'permissions': (CMFCorePermissions.View,)
               },)

    cp_view = Composite.__call__

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid)
        Composite.__init__(self)
        
    def getLayout(self):
        # refresh vocabulary
        composite_tool = getToolByName(self, TOOL_ID)
        layouts = composite_tool.layouts.objectValues('CompositePack Viewlet')
        template_ids = [layout.getTemplate().getId() for layout in layouts]
        self.schema['layout'].vocabulary = template_ids
        return self.getField('layout').get(self)
      
    def setLayout(self,viewlet_id):
        composite_tool = getToolByName(self, TOOL_ID)
        ## fix me for no / in template path
        path = composite_tool.layouts[viewlet_id].getTemplate_path()
        template_path = "/".join(path.split('/')[:-1])
        template_id = path.split('/')[-1]
        portal = getToolByName(self, 'portal_url').getPortalObject()
        source = portal.restrictedTraverse(template_path)
        objs=source.manage_copyObjects([template_id,])
        self.manage_pasteObjects(cb_copy_data=objs)
        
        #import pdb; pdb.set_trace()
        self.template_path = template_id
        
        self.getField('layout').set(self, viewlet_id)
       
registerType(CMFCompositePage, PROJECTNAME)
