# $Id: __init__.py,v 1.2 2003/07/28 02:12:28 plonista Exp $
# $Source: /home/hazmat/projects/psvn/collective/CMFFormController/__init__.py,v $
__version__ = "$Revision: 1.2 $"[11:-2]
"""Initialize CMFFormController"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import registerIcon, ToolInit

from config import *
import ControlledPageTemplate, FSControlledPageTemplate
import ControlledPythonScript, FSControlledPythonScript
import FormController
from Actions import RedirectTo, TraverseTo, RedirectToAction, TraverseToAction

# Make the skins available as DirectoryViews
# registerDirectory('skins', globals())

def initialize(context):
    tools = (FormController.FormController,)
    ToolInit('Form Controller Tool', tools=tools,
             product_name='CMFFormController', icon='tool.gif',
            ).initialize( context )
    context.registerClass(
        ControlledPageTemplate.ControlledPageTemplate,
        constructors=(ControlledPageTemplate.manage_addControlledPageTemplateForm,
                      ControlledPageTemplate.manage_addControlledPageTemplate),
        icon='www/cpt.gif',
        )
    context.registerClass(
        ControlledPythonScript.ControlledPythonScript,
        constructors=(ControlledPythonScript.manage_addControlledPythonScriptForm,
                      ControlledPythonScript.manage_addControlledPythonScript),
        icon='www/cpy.gif',
        )
    registerIcon(FSControlledPageTemplate.FSControlledPageTemplate,
                 'www/cpt.gif', globals())
    registerIcon(FSControlledPythonScript.FSControlledPythonScript,
                 'www/cpy.gif', globals())
