# Customizes the Plone site so CMFMember is installed and ready to use
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy import ICustomizationPolicy
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore.utils import getToolByName

def register(context, app_state):
    addPolicy('Plone site with CMFMember', PloneWithCMFMemberSitePolicy())

class PloneWithCMFMemberSitePolicy(DefaultCustomizationPolicy):
    """ Customizes the Plone site so CMFMember is installed and ready to use """
    __implements__ = ICustomizationPolicy

    availableAtConstruction = True
    
    def customize(self, portal):
        DefaultCustomizationPolicy().customize(portal)
        
        from Products.CMFMember.Extensions.Install import install as install_cmfmember
        install_cmfmember(portal)
        portal.cmfmember_control.upgrade(swallow_errors=0)        

        