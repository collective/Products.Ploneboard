from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate as BaseClass

import Globals
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.CMFCorePermissions import ManagePortal, View
from Products.CMFCore.utils import getToolByName
from ControlledBase import ControlledBase
from ControllerState import ControllerState
from ValidationError import ValidationError
from BaseControlledPageTemplate import BaseControlledPageTemplate
from FormAction import FormActionContainer
from FormValidator import FormValidatorContainer

import sys
from urllib import quote

# ###########################################################################
# Product registration and Add support
manage_addControlledPageTemplateForm = PageTemplateFile('www/cptAdd', globals())
manage_addControlledPageTemplateForm.__name__='manage_addControlledPageTemplateForm'


def manage_addControlledPageTemplate(self, id, title=None, text=None,
                                    REQUEST=None, submit=None):
    """Add a Controlled Page Template with optional file content."""

    id = str(id)
    if REQUEST is None:
        self._setObject(id, ControlledPageTemplate(id, text))
        ob = getattr(self, id)
        if title:
            ob.pt_setTitle(title)
        return ob
    else:
        file = REQUEST.form.get('file')
        headers = getattr(file, 'headers', None)
        if headers is None or not file.filename:
            zpt = ControlledPageTemplate(id)
        else:
            zpt = ControlledPageTemplate(id, file, headers.get('content_type'))

        self._setObject(id, zpt)

        try:
            u = self.DestinationURL()
        except AttributeError:
            u = REQUEST['URL1']

        if submit == " Add and Edit ":
            u = "%s/%s" % (u, quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''

# ###########################################################################
class ControlledPageTemplate(BaseClass, BaseControlledPageTemplate):

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    
    manage_options = (BaseClass.manage_options[:2] + \
        ({'label':'Validation',
          'action':'manage_formValidatorsForm'}, \
         {'label':'Actions',
          'action':'manage_formActionsForm'},) +
        BaseClass.manage_options[2:])

    meta_type = 'Controlled Page Template'

    def __init__(self, *args, **kwargs):
        self.validators = FormValidatorContainer()
        self.actions = FormActionContainer()
        return ControlledPageTemplate.inheritedAttribute('__init__')(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._call(ControlledPageTemplate.inheritedAttribute('__call__'), *args, **kwargs)


Globals.InitializeClass(ControlledPageTemplate)