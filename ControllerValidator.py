##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Controller Python Scripts Product

This product provides support for Script objects containing restricted
Python code.
"""

__version__='$Revision: 1.4 $'[11:-2]

import sys, os, re
from Globals import package_home
import AccessControl, OFS
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from urllib import quote
from Shared.DC.Scripts.Script import BindingsUI
from AccessControl import getSecurityManager
from OFS.History import Historical
from OFS.Cache import Cacheable
from zLOG import LOG, ERROR, INFO, PROBLEM
from Products.CMFCore.utils import getToolByName
from Script import PythonScript
from ControllerBase import ControllerBase
from FormAction import FormActionContainer

# Track the Python bytecode version
import imp
Python_magic = imp.get_magic()
del imp

# This should only be incremented to force recompilation.
Script_magic = 3
_log_complaint = (
    'Some of your Scripts have stale code cached.  Since Zope cannot'
    ' use this code, startup will be slightly slower until these Scripts'
    ' are edited. You can automatically recompile all Scripts that have'
    ' this problem by visiting /manage_addProduct/PythonScripts/recompile'
    ' of your server in a browser.')

_default_file = os.path.join(package_home(globals()),
                             'www', 'default_vpy')

_marker = []  # Create a new marker object

# ###########################################################################
# Product registration and Add support
manage_addControllerValidatorForm = PageTemplateFile('www/vpyAdd', globals())
manage_addControllerValidatorForm.__name__='manage_addControllerValidatorForm'

def manage_addControllerValidator(self, id, REQUEST=None, submit=None):
    """Add a Python script to a folder.
    """
    id = str(id)
    id = self._setObject(id, ControllerValidator(id))
    if REQUEST is not None:
        file = REQUEST.form.get('file', '')
        if type(file) is not type(''): file = file.read()
        if not file:
            file = open(_default_file).read()
        self._getOb(id).write(file)
        try: u = self.DestinationURL()
        except: u = REQUEST['URL1']
        if submit==" Add and Edit ": u="%s/%s" % (u,quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''


class ControllerValidator(PythonScript, ControllerBase):
    """Web-callable scripts written in a safe subset of Python.

    The function may include standard python code, so long as it does
    not attempt to use the "exec" statement or certain restricted builtins.
    """

    meta_type='Controller Validator'

    manage_options = (
        {'label':'Edit',
         'action':'ZPythonScriptHTML_editForm',
         'help': ('PythonScripts', 'PythonScript_edit.stx')},
        ) + BindingsUI.manage_options + (
        {'label':'Test',
         'action':'ZScriptHTML_tryForm',
         'help': ('PythonScripts', 'PythonScript_test.stx')},
#        {'label':'Actions','action':'manage_formActionsForm'},             
        {'label':'Proxy',
         'action':'manage_proxyForm',
         'help': ('OFSP','DTML-DocumentOrMethod_Proxy.stx')},
        ) + Historical.manage_options + SimpleItem.manage_options + \
        Cacheable.manage_options

    security = AccessControl.ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected('View', '__call__')

    security.declareProtected('View management screens',
      'ZPythonScriptHTML_editForm', 'manage_main', 'read',
      'ZScriptHTML_tryForm', 'PrincipiaSearchSource',
      'document_src', 'params', 'body')

    security.declareProtected('Change Python Scripts',
      'ZPythonScriptHTML_editAction',
      'ZPythonScript_setTitle', 'ZPythonScript_edit',
      'ZPythonScriptHTML_upload', 'ZPythonScriptHTML_changePrefs')


    def __init__(self, *args, **kwargs):
#        self.actions = FormActionContainer()
        return ControllerValidator.inheritedAttribute('__init__')(self, *args, **kwargs)


    def __call__(self, *args, **kwargs):
        result = ControllerValidator.inheritedAttribute('__call__')(self, *args, **kwargs)
#        if getattr(result, '__class__', None) == ControllerState and not result._isValidating():
#            return self.getNext(result, self.REQUEST)
        return result

    def _getState(self):
        return getToolByName(self, 'portal_form_controller').getState(self, is_validator=1)
