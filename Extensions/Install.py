from Products.CMFCore.utils import getToolByName

def install(self, reinstall=False):
    tool=getToolByName(self, "portal_setup")

    plone_base_profileid = "profile-CMFPlone:plone"
    # Small trick to enforce loading of the right import steps
    tool.setImportContext(plone_base_profileid)
    tool.setImportContext("profile-Products.Ploneboard:default")
    tool.runAllImportSteps(purge_old=False)

    tool.setImportContext(plone_base_profileid)
