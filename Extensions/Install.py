""" Installation script for the skins, content types and form_controller transitions
"""

from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFFormController.FormAction import FormActionKey

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from cStringIO import StringIO
#import string

from Products.ATBiblioList import PROJECTNAME, GLOBALS
from Products.ATBiblioList.config import formcontroller_transitions
from Products.ATBiblioList.formatters.MinimalFormat import MinimalFormat

#
# Install functions
#
def addCustomFormControllerTransitions(self, out):
    """ Add predefined custom form_controller transitions
    """
    container = getToolByName(self, 'portal_form_controller')
    for transition in formcontroller_transitions:
        container.addFormAction(**transition)
    out.write("Added custom transitions to 'portal_form_controller'")

def fixContentTab(self,out):
    pp = getToolByName(self, 'portal_properties', None)
    if pp and hasattr(pp, 'site_properties'):
        use_folder_tabs = pp.site_properties.getProperty('use_folder_tabs', [])
        if 'PresentationFolder' not in use_folder_tabs:
            use_folder_tabs += ('PresentationFolder', )
            pp.site_properties.manage_changeProperties(
	        {'use_folder_tabs' : use_folder_tabs},
                )

def setupTool(self, out):
    """ adds the bibliolist tool to the portal root folder
    """
    if hasattr(self, 'portal_bibliolist'):
        self.manage_delObjects(['portal_bibliolist'])
        out.write('Deleting old tool; make sure you repeat customizations.')
    addTool = self.manage_addProduct['ATBiblioList'].manage_addTool
    addTool('BiblioList Tool', None)
    out.write("\nAdded the bibliolist tool to the portal root folder.\n")

def install(self):
    """ Main install function
    """
    out=StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    addCustomFormControllerTransitions(self, out)
    
    fixContentTab(self,out)

    setupTool(self,out)
    
    out.write('Installation completed.\n')
    return out.getvalue()

    
#
# Uninstall functions
#
def removeCustomFormControllerTransitions(self, out):
    fc = getToolByName(self, 'portal_form_controller')
    #BAAH no Python API for deleting actions in FormController
    #lets get our hands dirty
    container = fc.actions
    for transition in formcontroller_transitions: 
        try:
            container.delete(FormActionKey(transition['object_id'],
                                           transition['status'],
                                           transition['context_type'],
                                           transition['button'],
                                           ))
        except KeyError: pass
    out.write("Removed custom form controller actions")    


def uninstall(self):
    """ Uninstall the product
    """
    out = StringIO()

    removeCustomFormControllerTransitions(self, out)
    
    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
