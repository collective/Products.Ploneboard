import os
import Globals
from AccessControl import ClassSecurityInfo
from Products.CompositePage.designuis import CommonUI
from Products.CompositePage.rawfile import RawFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

_plone = os.path.join(os.path.dirname(__file__), 'plone')

class PloneUI(CommonUI):
    """Page design UI meant to fit Plone.

    Adds Plone-specific scripts and styles to a page.
    """
    security = ClassSecurityInfo()

    workspace_view_name = 'view'

    security.declarePublic('plone_edit_js')
    plone_edit_js = RawFile('plone_edit.js', 'text/javascript', _plone)

    header_templates = CommonUI.header_templates + (
        PageTemplateFile('header.pt', _plone),)
    top_templates = CommonUI.top_templates + (
        PageTemplateFile('top.pt', _plone),)
    bottom_templates = (PageTemplateFile('bottom.pt', _plone),
                        ) 

Globals.InitializeClass(PloneUI)
