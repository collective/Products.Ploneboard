from zope.app.tests import placelesssetup

from Products.Five import zcml
import Products.Five
import Products.ATContentTypes

def disableScriptValidators(portal):
    from Products.CMFFormController.FormController import ANY_CONTEXT, ANY_BUTTON
    scripts = ['add_comment_script', 'add_conversation_script', 'add_forum_script']
    try:
        for v in portal.portal_skins.ploneboard_scripts.objectValues():
            if v.id in scripts:
                v.manage_doCustomize('custom')
                portal.portal_form_controller.addFormValidators(v.id, ANY_CONTEXT, ANY_BUTTON, [])
    except:
        pass

def caSetUp(self):
    """Setup component architecture"""
    
    # some nasty Five bug in old Five versions needs _context reset
    Products.Five.zcml._context = None
    
    placelesssetup.setUp()
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('permissions.zcml', Products.Five)
    try:
        zcml.load_config('bridge.zcml', Products.ATContentTypes)
    except IOError:
        # In Plone 2.5 and up, this file doesn't exist
        pass
    zcml.load_config('configure.zcml', Products.Ploneboard)

def caTearDown(self):
    """Tear down component architecture"""

    placelesssetup.tearDown()
