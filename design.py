##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Plone UI for Composite Page design view.

$Id: design.py,v 1.6 2004/06/22 07:47:45 godchap Exp $
"""
import os
import Globals
from AccessControl import ClassSecurityInfo
from Products.CompositePage.designuis import CommonUI
from Products.CompositePage.rawfile import RawFile
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
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
    target_image = RawFile('target_image.gif', 'image/gif', _plone)
    target_image_hover = RawFile('target_image.gif', 'image/gif', _plone)
    target_image_active = RawFile('target_image.gif', 'image/gif', _plone)

    editstyles_css = FSDTMLMethod("editstyles.css", os.path.join(_plone,
        "editstyles.css"))
    pdstyles_css = FSDTMLMethod("pdstyles.css", os.path.join(_plone,
        "pdstyles.css"))

    header_templates = CommonUI.header_templates + (
        PageTemplateFile('header.pt', _plone),)
    top_templates = CommonUI.top_templates + (
        PageTemplateFile('top.pt', _plone),)
    bottom_templates = (PageTemplateFile('bottom.pt', _plone),
                        ) 

Globals.InitializeClass(PloneUI)
