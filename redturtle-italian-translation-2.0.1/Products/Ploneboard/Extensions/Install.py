from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

def install(self, reinstall=False):
    tool=getToolByName(self, "portal_setup")

    if getFSVersionTuple()[0]>=3:
        tool.runAllImportStepsFromProfile(
                "profile-Products.Ploneboard:ploneboard",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-Products.Ploneboard:default")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)
