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
