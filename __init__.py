# $Id: __init__.py,v 1.1 2003/07/04 20:11:59 plonista Exp $
# $Source: /home/hazmat/projects/psvn/collective/CMFFormController/__init__.py,v $
__version__ = "$Revision: 1.1 $"[11:-2]
"""Initialize CMFFormController"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from Products.CMFCore.utils import ToolInit

from config import *
import ControlledPageTemplate, FSControlledPageTemplate
import ControlledPythonScript, FSControlledPythonScript
import FormController
from Actions import RedirectTo, TraverseTo, RedirectToAction, TraverseToAction

# Make the skins available as DirectoryViews
# registerDirectory('skins', globals())

def initialize(context):
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
    utils.registerIcon(FSControlledPageTemplate.FSControlledPageTemplate,
                       'www/cpt.gif', globals())
    utils.registerIcon(FSControlledPythonScript.FSControlledPythonScript,
                       'www/cpy.gif', globals())
    tools = (FormController.FormController,)
    ToolInit('Form Controller Tool', tools=tools,
             product_name='CMFFormController', icon='tool.gif',
            ).initialize( context )
