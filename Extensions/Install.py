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

#
# Elements to be installed
#
#
custom_formcontroller_transitions = (
        {'object_id'    : 'base_edit',
         'status'       : 'success',
         'context_type' : '',
         'button'       : 'reference_search',
         'action_type'  : 'traverse_to',
         'action_arg'   : 'string:base_edit'},

        {'object_id'    : 'base_edit',
         'status'       : 'success',
         'context_type' : '',
         'button'       : 'reference_add',
         'action_type'  : 'traverse_to',
         'action_arg'   : 'string:bibliography_list_edit'},

        {'object_id'    : 'base_edit',
         'status'       : 'success',
         'context_type' : '',
         'button'       : 'reference_delete',
         'action_type'  : 'traverse_to',
         'action_arg'   : 'string:bibliography_list_edit'},
        
        {'object_id'    : 'base_edit',
         'status'       : 'success',
         'context_type' : '',
         'button'       : 'reference_up',
         'action_type'  : 'traverse_to',
         'action_arg'   : 'string:bibliography_list_edit'},

        {'object_id'    : 'base_edit',
         'status'       : 'success',
         'context_type' : '',
         'button'       : 'reference_down',
         'action_type'  : 'traverse_to',
         'action_arg'   : 'string:bibliography_list_edit'},
                                     )

#
# Install functions
#
def addCustomFormControllerTransitions(self, out):
    """ Add predefined custom form_controller transitions
    """
    container = getToolByName(self, 'portal_form_controller')
    for transition in custom_formcontroller_transitions:
        container.addFormAction(**transition)
    out.write("Added custom transitions to 'portal_form_controller'")

def fixContentTab(self):
    pp = getToolByName(self, 'portal_properties', None)
    if pp and hasattr(pp, 'site_properties'):
        use_folder_tabs = pp.site_properties.getProperty('use_folder_tabs', [])
        if 'PresentationFolder' not in use_folder_tabs:
            use_folder_tabs += ('PresentationFolder', )
            pp.site_properties.manage_changeProperties(
	        {'use_folder_tabs' : use_folder_tabs},
                )
    
def install(self):
    """ Main install function
    """
    out=StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    addCustomFormControllerTransitions(self, out)
    
    fixContentTab(self)
    
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
    for transition in custom_formcontroller_transitions: 
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
