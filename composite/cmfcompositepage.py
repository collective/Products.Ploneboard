##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Plone Composite Page : 
   design view UI in line with Plone UI

$Id: cmfcompositepage.py,v 1.17 2004/06/22 07:47:46 godchap Exp $
"""
from cgi import escape

from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CompositePage.interfaces import IComposite
from Products.CompositePage.composite import Composite, SlotGenerator
from Products.CompositePage.slot import Slot, getIconURL
from Products.CompositePack.config import PROJECTNAME, TOOL_ID
from Products.CMFCore.CMFCorePermissions import setDefaultRoles
from Products.CMFCore import CMFCorePermissions 
from Products.CMFCore.utils import getToolByName



edit_tag = '''<div class="slot_element" source_path="%s" icon="%s" title="%s"
allowed_viewlets_ids="%s" allowed_viewlets_titles="%s" full_path="%s">
<div class="slot_element_body">%s</div>
</div>'''


class PackSlot(Slot):
   __occams_gestalt__ = 1 

   def _render_editing(self, obj, text, icon_base_url):
        o2 = obj.dereference()
        icon = escape(getIconURL(o2, icon_base_url).encode('utf8'))
        title = escape(o2.title_and_id().encode('utf8'))
        path = escape('/'.join(obj.getPhysicalPath()))
        full_path = obj.absolute_url()
        composite_tool = getToolByName(self, TOOL_ID)
        viewlets_info = composite_tool.getViewletsFor(o2)
        allowed_viewlets_ids = []
        allowed_viewlets_titles = []
        if viewlets_info:
            allowed_viewlets_ids.append(viewlets_info['default']["id"])
            allowed_viewlets_titles.append(viewlets_info['default']["viewlet"].title_or_id())
            for viewlet in viewlets_info['viewlets']:
                allowed_viewlets_ids.append(viewlet["id"])
                allowed_viewlets_titles.append(viewlet["viewlet"].title_or_id())
        allowed_viewlets_ids = " ".join(allowed_viewlets_ids)
        allowed_viewlets_ids = allowed_viewlets_ids.encode('utf8')
        allowed_viewlets_titles = "%".join(allowed_viewlets_titles)
        allowed_viewlets_titles = allowed_viewlets_titles.encode('utf8')
        result = edit_tag % (path,
                           icon,
                           title,
                           allowed_viewlets_ids,
                           allowed_viewlets_titles,
                           full_path,
                           text)
        return result

class PackSlotGenerator(SlotGenerator):
    _slot_class = PackSlot

class PackComposite(Composite):
    slots = PackSlotGenerator()


DesignCompo = 'Design Composite Page'
setDefaultRoles(DesignCompo, ('Manager',))

class CMFCompositePage(BaseFolder, PackComposite):
    """A basic, Archetypes-based Composite Page
    """
    __implements__ = BaseFolder.__implements__ + (IComposite,)
    meta_type = portal_type = 'CMF Composite Page'
    archetype_name = 'Navigation Page'

    security = ClassSecurityInfo()
    
    __occams_gestalt__ = 1
    use_folder_tabs = 0

    schema = BaseSchema + Schema((
                       StringField('layout', 
                                   widget=SelectionWidget(label='Layout',
                                                          format='select'),
                                  ) 
                    ))

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'cp_view',
                'permissions': (CMFCorePermissions.View,)
               },
               {'id': 'design',
                'name': 'Design',
                'action': 'string:${object_url}/design_view',
                'condition':'object/getLayout',
                'permissions': (DesignCompo,)
               },
               )

    factory_type_information={
        'content_icon':'composite.gif',
        }

    cp_view = Composite.__call__

    security.declareProtected( DesignCompo, 'design_view')
    def design_view(self):
        '''design view for Plone
        '''
        return self.design(ui='plone')

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid)
        Composite.__init__(self)
        f = Folder()
        f._setId("titles")
        self._setObject(f.getId(), f)
        
    def getLayout(self):
        # refresh vocabulary
        composite_tool = getToolByName(self, TOOL_ID)
        layouts = composite_tool.layouts.objectValues('CompositePack Viewlet')
        layouts = [(layout.getId(), layout.title_or_id()) for layout in layouts]
        self.schema['layout'].vocabulary = DisplayList(layouts)
        return self.getField('layout').get(self)
      
    def setLayout(self, viewlet_id):
        composite_tool = getToolByName(self, TOOL_ID)
        ## fix me for no / in template path
        path = composite_tool.layouts[viewlet_id].getSkin_method()
        template_path = "/".join(path.split('/')[:-1])
        template_id = path.split('/')[-1]
        
        self.template_path = template_id
        
        self.getField('layout').set(self, viewlet_id)

    def getPathFromPortal(self):
        portal_object = getToolByName(self, 'portal_url').getPortalObject()
        phypath_from_portal = self.getPhysicalPath()[len(portal_object.getPhysicalPath()):];
        return '/'.join(phypath_from_portal)

    def incrementVersion(self, checkin_message=''):
        if self._occams_installed():
            self.getCurrentGateway().getStageMap().incrementVersion(self,
                    checkin_message=checkin_message)            
        else:
            pass
           
    def _occams_installed(self):
        return hasattr(self, 'getCurrentGateway')
        
registerType(CMFCompositePage, PROJECTNAME)
