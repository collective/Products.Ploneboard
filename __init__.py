# $Id: __init__.py,v 1.3 2003/09/23 17:57:56 plonista Exp $
# $Source: /home/hazmat/projects/psvn/collective/CMFFormController/__init__.py,v $
__version__ = "$Revision: 1.3 $"[11:-2]
"""Initialize CMFFormController"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import registerIcon, ToolInit

from config import *
import ControllerPageTemplate, FSControllerPageTemplate
import ControllerPythonScript, FSControllerPythonScript
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
    registerIcon(FSControllerPageTemplate.FSControllerPageTemplate,
                 'www/cpt.gif', globals())
    registerIcon(FSControllerPythonScript.FSControllerPythonScript,
                 'www/cpy.gif', globals())
