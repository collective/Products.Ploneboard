from cStringIO import StringIO
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFFormController import GLOBALS
import string


def install(self):
    out = StringIO()

    if not hasattr(self, 'portal_form_controller'):
        addTool = self.manage_addProduct['CMFFormController'].manage_addTool
        addTool('Form Controller Tool')
        out.write('Added Form Controller Tool\n')
#    portal_form_controller = self.portal_form_controller

    return out.getvalue()
