from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Acquisition import Implicit, aq_base
from cgi import escape

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression

class ContentPanelsTool( UniqueObject, SimpleItem, PropertyManager, ActionsTool ):

    id = 'portal_contentpanels'
    meta_type = 'ContentPanels Tool'
    _actions = tuple()

    action_providers = ('portal_contentpanels',)
    security = ClassSecurityInfo()

    manage_options = (ActionProviderBase.manage_options +
                #     ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                #     , 
                #     ) + 
                     PropertyManager.manage_options +
                     SimpleItem.manage_options)

    def __init__(self):
        self._setProperty('Default', 'defaultPortletWrapper', 'string')
        self._setProperty('No Title', 'notitlePortletWrapper', 'string')
        self._setProperty('ZopeZen', 'zopezenPortletWrapper', 'string')
        self._setProperty('Default Box', 'boxPortletWrapper', 'string')

    def valid_property_id(self, id):
        if not id or id[:1]=='_' or (id[:3]=='aq_') \
           or hasattr(aq_base(self), id) or escape(id) != id:
            return 0
        return 1

    security.declarePublic('getPanelSkins')
    def getPanelSkins(self):
        return filter(lambda i: (i[0] != 'title'), list(self.propertyItems()))

    def installActions(self, actions=[]):
        for action in actions:
            self.addAction(action[0],action[1],action[2],
                           action[3],action[4],action[5],action[6])


    security.declarePublic('getViewletName')
    def getViewletName(self, viewletId):
        """get a name of a viewlet"""
        for action in self._listAllActions():
            if action['id'] == viewletId:
                return action['name']
        return None

    security.declarePublic('getViewletPath')
    def getViewletPath(self, viewletId):
        """get a name of a viewlet"""
        for action in self._listAllActions():
            if action['id'] == viewletId:
                return action['url']
        return None

    def _listAllActions(self):
        """this method should be refined. all actions can be cached"""
        all_actions = self.listFilteredActions()
        actions = []
        for a in all_actions.values():
            actions = actions + a
        return actions

InitializeClass( ContentPanelsTool )
