# -*- coding: iso-8859-1 -*-

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: SchemaEditorTool.py,v 1.1 2004/12/28 10:50:14 ajung Exp $
"""

from Globals import DTMLFile, InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from SchemaEditor import SchemaEditor

from config import TOOL_NAME

class SchemaEditorTool(SimpleItem, SchemaEditor):
    """ SchemaEditorTool"""

    meta_type = 'ATSchemaEditorTool'
    id = TOOL_NAME

    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):
        self._clear()               # SchemaEditor._clear()

InitializeClass(SchemaEditorTool)


manage_addSchemaEditorToolForm = DTMLFile('dtml/addSchemaEditorTool', globals())

def manage_addSchemaEditorTool(self, RESPONSE=None):
    """Add a new SchemaEditorTool """


    tool = SchemaEditorTool()
    self._setObject(TOOL_NAME, tool)
    tool = self._getOb(TOOL_NAME)
    tool = tool.__of__(self)

    if RESPONSE:
        RESPONSE.redirect(self.absolute_url() + '/manage_main')        
