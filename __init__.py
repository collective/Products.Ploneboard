# $Id: __init__.py,v 1.5 2003/10/16 15:18:50 plonista Exp $
# $Source: /home/hazmat/projects/psvn/collective/CMFFormController/__init__.py,v $
__version__ = "$Revision: 1.5 $"[11:-2]
"""Initialize CMFFormController"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import registerIcon, ToolInit

from config import *
import ControllerPageTemplate, FSControllerPageTemplate
import ControllerPythonScript, FSControllerPythonScript
import ControllerValidator, FSControllerValidator
import FormController
from Actions import RedirectTo, TraverseTo, RedirectToAction, TraverseToAction

GLOBALS = globals()

# Make the skins available as DirectoryViews
# registerDirectory('skins', globals())

def initialize(context):
    tools = (FormController.FormController,)
    ToolInit('Form Controller Tool', tools=tools,
             product_name='CMFFormController', icon='tool.gif',
            ).initialize( context )
    context.registerClass(
        ControllerPageTemplate.ControllerPageTemplate,
        constructors=(ControllerPageTemplate.manage_addControllerPageTemplateForm,
                      ControllerPageTemplate.manage_addControllerPageTemplate),
        icon='www/cpt.gif',
        )
    context.registerClass(
        ControllerPythonScript.ControllerPythonScript,
        constructors=(ControllerPythonScript.manage_addControllerPythonScriptForm,
                      ControllerPythonScript.manage_addControllerPythonScript),
        icon='www/cpy.gif',
        )
    context.registerClass(
        ControllerValidator.ControllerValidator,
        constructors=(ControllerValidator.manage_addControllerValidatorForm,
                      ControllerValidator.manage_addControllerValidator),
        icon='www/vpy.gif',
        )
    registerIcon(FSControllerPageTemplate.FSControllerPageTemplate,
                 'www/cpt.gif', globals())
    registerIcon(FSControllerPythonScript.FSControllerPythonScript,
                 'www/cpy.gif', globals())
    registerIcon(FSControllerValidator.FSControllerValidator,
                 'www/vpy.gif', globals())

