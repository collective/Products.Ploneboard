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
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression

class ContentPanelsTool( UniqueObject, SimpleItem, PropertyManager, ActionProviderBase ):

#    __implements__ = (ActionProviderBase.__implements__)

    id = 'portal_contentpanels'
    meta_type = 'ContentPanels Tool'
    _actions = (ActionInformation(id='latest_updates_viewlet'
                                , title='Latest Updates'
                                , action=Expression(
                text='string:here/viewlets_folder_recent/macros/base_portlet')
                                , condition=Expression(
                text='python: object.isPrincipiaFolderish')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='default_viewlet'
                                , title='Default Viewlet'
                                , action=Expression(
                text='string:here/viewlet_default/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='my_recent_changes'
                                , title='My Recent Updates'
                                , action=Expression(
                text='string:here/portlet_mychanges/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_favorites'
                                , title='My Favorites'
                                , action=Expression(
                text='string:here/portlet_favorites/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_calendar'
                                , title='Calendar'
                                , action=Expression(
                text='string:here/portlet_calendar/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_login'
                                , title='Login'
                                , action=Expression(
                text='string:here/portlet_login/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_related'
                                , title='Related'
                                , action=Expression(
                text='string:here/portlet_related/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_events'
                                , title='Events'
                                , action=Expression(
                text='string:here/portlet_events/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_navigation'
                                , title='Navigation'
                                , action=Expression(
                text='string:here/portlet_navigation/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_review'
                                , title='Review List'
                                , action=Expression(
                text='string:here/portlet_review/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_news'
                                , title='News'
                                , action=Expression(
                text='string:here/portlet_news/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_language'
                                , title='Language'
                                , action=Expression(
                text='string:here/portlet_language/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )
               ,
               ActionInformation(id='portlet_recent'
                                , title='Recent Published'
                                , action=Expression(
                text='string:here/portlet_recent/macros/portlet')
                                , condition=Expression(
                text='python: 1')
                                , permissions=('View',)
                                , category='panel_viewlets'
                                , visible=1
                                 )

               )

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

InitializeClass( ContentPanelsTool )
