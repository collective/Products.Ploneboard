# Customizes the Plone site so CMFMember is installed and ready to use
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy import ICustomizationPolicy
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore.utils import getToolByName

def register(context, app_state):
    addPolicy('CMFMember Site', CMFMemberSitePolicy())

class CMFMemberSitePolicy(DefaultCustomizationPolicy):
    """ Customizes the Plone site so CMFMember is installed and ready to use """
    __implements__ = ICustomizationPolicy

    availableAtConstruction = True
    
    def customize(self, portal):
        DefaultCustomizationPolicy().customize(portal)
        self.setupCMFMember(portal)

    def setupCMFMember(self, portal):
        portal.portal_quickinstaller.installProduct("CMFMember")
        portal.cmfmember_control.upgrade(swallow_errors=0) 
