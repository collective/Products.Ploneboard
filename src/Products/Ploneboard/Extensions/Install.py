from Products.CMFCore.utils import getToolByName


def install(self, reinstall=False):
    tool = getToolByName(self, "portal_setup")
    tool.runAllImportStepsFromProfile(
            "profile-Products.Ploneboard:default",
            purge_old=False)


def uninstall(self):
    portal_setup = getToolByName(self, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile(
        'profile-Products.Ploneboard:uninstall',
        purge_old=False)
