##############################################################################
#
# Copyright (c) 2002 ZopeChina Corporation (http://zopechina.com). All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Implement the content panels content type."""

import string
import urlparse

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalContent import PortalContent, NoWL
from Products.CMFCore.PortalContent import ResourceLockedError
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import keywordsplitter

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

factory_type_information = ( {'id': 'ContentPanels',
                            'content_icon': 'contentpanels_icon.gif',
                            'meta_type': 'CMF Content Panels',
                            'description': """ContentPanels is a portlet content to build composite page.""", 
                            'product': 'CMFContentPanels',
                            'factory': 'addContentPanels',
                                'immediate_view': 'contentpanels_edit_form',
                            'actions': ({'id': 'view',
                                        'name': 'View',
                                        'action': 'contentpanels_view',
                                        'permissions': (CMFCorePermissions.View,)
                                         }
                                      , {'id': 'edit',
                                        'name': 'Edit',
                                        'action': 'contentpanels_edit_form',
                                        'permissions': (CMFCorePermissions.ModifyPortalContent,)
                                         }
                                      , {'id': 'config',
                                        'name': 'Config',
                                        'action': 'contentpanels_config_form',
                                        'permissions': (CMFCorePermissions.ModifyPortalContent,)
                                         }
                                       , { 'id'            : 'metadata'
                                          , 'name'          : 'Metadata'
                                          , 'action'        : 'metadata_edit_form'
                                          , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
                                          }
                                     )
                            },
                        )

def addContentPanels( self
           , id
           , title=''
           , description=''
           ):
    o=ContentPanels( id, title, description)
    self._setObject(id,o)


class ContentPanels(PortalContent, DefaultDublinCoreImpl):
    """
    content panels class.
    """

    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )

    meta_type = 'CMF Content Panels'
    effective_date = expiration_date = None
    panelsConfig = []
    
    security = ClassSecurityInfo()

    def __init__(self, id, title='', description=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.description=description
        self.clearPanels()
        self.addPage()

    def clearPanels(self):
        self.panelsConfig = []
        self._p_changed = 1

    security.declarePublic('toRelativePath')
    def toRelativePath(self, panelObjectPath):
        """ regenerate panelObjectPath, make it a relative path.
        path may be relative to this contentpanels or relate to the portal.
        - if panelObjectPath == '.', it means contentpanels it self
        - if panelObjectPath start with './', it means relative to portal
        - else, it means rlative to the folderish context of this contentpanels(can use acquisition)
        see also: getPanelObject
        """
        panelContent = self.getPanelObject(panelObjectPath)
        if panelContent == None: 
            panelContent = self 

        folderContext = self
        if not self.isPrincipiaFolderish:
            folderContext = self.aq_parent

        relativePath = self.portal_url.getRelativeContentURL(panelContent)
        if panelContent == self:
            relativePath = '.'
        else:
            folderContextPath = self.portal_url.getRelativeContentURL(folderContext) + '/'
            if relativePath.startswith(folderContextPath):
                relativePath = './' + panelObjectPath[len(folderContextPath):]
        return relativePath

    def getPanelObject(self, objectPath):
      """get panel object by path.
         if panelObjectPath == '.', it means contentpanels it self
         if panelObejctPath start with './', it means relative to this contentpanels
         else, it means rlative to the portal
         see also: toRelativePath
      """
      panelObject = None
      try:
        if objectPath in ['.', '/']:  # '.'means the contentpanels it self
          panelObject = self
        elif objectPath.find('./') == 0:  # relative path to the folderish context
          objectPath = objectPath[2:]

          folderContext = self
          if not self.isPrincipiaFolderish:
            folderContext = self.aq_parent

          panelObject = folderContext.restrictedTraverse(objectPath) 
        else :
          panelObject = self.portal_url.getPortalObject().restrictedTraverse(objectPath)
      except:
        panelObject = None
      return panelObject


    security.declarePublic('getPanel')
    def getPanel(self, objectPath, panelSkin, viewletId):
        """ get a panel """
        panelObject = self.getPanelObject(objectPath)

        # get viewlet infomation
        viewletPath = self.portal_contentpanels.getViewletPath(viewletId)

        if viewletPath:
            return panelObject.base_panel(panelObject,
                              contentpanels=self,
                              panelSkin=panelSkin,
                              viewletPath=viewletPath)
        else:
            return None

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addPage' )
    def addPage(self, pageTitle='Untitled page', pageIndex=-1):
        """
        add a new page at pageIndex, it has two columns as default.
        if pageIndex is -1 then add at the end of the contentpanels
        return the new page index (from 0)
        """
        if pageIndex == -1:
            pageIndex = len(self.panelsConfig)
        self.panelsConfig.insert(pageIndex, {'pageColumns': [],
                         'pageTitle': pageTitle,
                         'pageWidth':'100%',
                         'pageCellSpace':'0',
                         'pageCellPad':'3',
                         'pageAlign':'center',
                         'pageStylesheetFixed':[],
                         'pageStylesheetDynamic':[]})

        # add two default columns for the new page
        self.addColumn(pageIndex)
        self.addColumn(pageIndex)
        self._p_changed = 1
        return pageIndex

    security.declareProtected( CMFCorePermissions.View, 'getPageTitles' )
    def getPageTitles(self):
        ''' get all the tilte of the pages '''
        titles = []
        for pageIndex in range(len(self.panelsConfig) ):
            titles.append(self.panelsConfig[pageIndex]['pageTitle'])
        return titles

    security.declareProtected( CMFCorePermissions.View, 'getPageInfo' )
    def getPageInfo(self, pageIndex, infoName):
        ''' get general info of the page '''
        return self.panelsConfig[pageIndex][infoName]

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changePageInfo' )
    def changePageInfo(self, pageIndex, pageTitle="", pageCellPad='', pageCellSpace='', pageWidth='', pageAlign=''):
        ''' change page's table info '''
        if pageCellPad == '':
            pageCellPad = '3'
        if pageCellSpace == '':
            pageCellSpace = '0'
        if pageWidth == '':
            pageWidth = '100%'
        if pageAlign == '':
            pageAlign = 'center'

        self.panelsConfig[pageIndex]['pageWidth']= pageWidth
        self.panelsConfig[pageIndex]['pageAlign']= pageAlign
        self.panelsConfig[pageIndex]['pageCellPad']= pageCellPad
        self.panelsConfig[pageIndex]['pageCellSpace']= pageCellSpace
        self.panelsConfig[pageIndex]['pageTitle']= pageTitle
        self._p_changed = 1

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'movePage')
    def movePage(self, pageIndex, toPage):
        """move a page from fromIndex to toIndex"""
        page = self.panelsConfig.pop(pageIndex)
        self.panelsConfig.insert(toPage, page)
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'deletePage' )
    def deletePage(self, pageIndex):
        ''' delete a page,
        return next page index to show'''
        nextPageIndex = pageIndex
        if len(self.panelsConfig) > 1:  # can't delete the last page!
            del self.panelsConfig[pageIndex]

            if pageIndex == len(self.panelsConfig):
                nextPageIndex = pageIndex - 1
        self._p_changed = 1
        return nextPageIndex

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addColumn' )
    def addColumn(self, pageIndex, columnIndex=-1):
        """add a new Column to 'pageIndex' at 'columnIndex'
        if 'columnIndex' is -1 then add to the end of the column'
        """
        if columnIndex == -1:
           columnIndex = len(self.panelsConfig[pageIndex]['pageColumns'])

        self.panelsConfig[pageIndex]['pageColumns'].insert(columnIndex, {'columnWidth': '0',
                                                            'columnPanels':[] })
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changeColumnWidth' )
    def changeColumnWidth(self, pageIndex, columnIndex, columnWidth):
        ''' change the width of a column '''
        if columnWidth == '':
            return None

        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnWidth'] = columnWidth
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'moveColumn')
    def moveColumn(self, pageIndex, columnIndex, toColumn):
        """move a column from 'fromIndex' to 'toIndex'"""
        column = self.panelsConfig[pageIndex]['pageColumns'].pop(columnIndex)
        self.panelsConfig[pageIndex]['pageColumns'].insert(toColumn, column)
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'deleteColumn' )
    def deleteColumn(self, pageIndex, columnIndex):
        '''# delete column'''
        if len(self.panelsConfig[pageIndex]['pageColumns']) > 1:
            del self.panelsConfig[pageIndex]['pageColumns'][columnIndex]
            self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addPanel' )
    def addPanel(self, pageIndex, columnIndex, panelIndex, panelObjectPath, panelObjectViewlet, panelSkin):
        ''' insert a new panel at panelIndex'''
        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'].\
                insert(panelIndex, {'panelSkin':panelSkin,
                        'panelObjectPath':panelObjectPath,
                        'panelObjectViewlet':panelObjectViewlet})
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'deletePanel' )
    def deletePanel(self, pageIndex, columnIndex, panelIndex):
        ''' delete a Panel '''
        del self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changePanel' )
    def changePanel(self, pageIndex, columnIndex, panelIndex, panelObjectPath='', panelObjectViewlet='', panelSkin=''):
        ''' change the skin of a existing panel '''
        
        if panelSkin:
            self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelSkin'] = panelSkin
        if panelObjectPath:
            self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelObjectPath'] = panelObjectPath
        if panelObjectViewlet:
            self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelObjectViewlet'] = panelObjectViewlet
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'movePanel')
    def movePanel(self, pageIndex, columnIndex, panelIndex, toColumn, toPanel):
        """move a panel from 'toIndex'"""
        if toColumn == -1: 
            toColumn = columnIndex
        if toPanel == -1: 
            toPanel = panelIndex

        panel = self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'].pop(panelIndex)
        toColumnLen = len(self.panelsConfig[pageIndex]['pageColumns'][toColumn]['columnPanels'])
        if toPanel > toColumnLen:
            toPanel = toColumnLen
        self.panelsConfig[pageIndex]['pageColumns'][toColumn]['columnPanels'].insert(toPanel, panel)
        self._p_changed = 1

InitializeClass(ContentPanels)
