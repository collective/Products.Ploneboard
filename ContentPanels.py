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
                            'description': """\
Content Panels is a portlet content to place multi-content to panels visully.""", 
                            'product': 'CMFContentPanels',
                            'factory': 'addContentPanels',
                                'immediate_view': 'contentpanels_edit_form',
                            'actions': ({'id': 'view',
                                        'name': 'view',
                                        'action': 'contentpanels_view',
                                        'permissions': (CMFCorePermissions.View,)
                                         , 'visible'   : 0
                                         }
                                      , {'id': 'edit',
                                        'name': 'configure',
                                        'action': 'contentpanels_edit_form',
                                        'permissions': (CMFCorePermissions.ModifyPortalContent,)
                                         , 'visible'   : 0
                                         }
                                       , { 'id'            : 'metadata'
                                          , 'name'          : 'Metadata'
                                          , 'action'        : 'metadata_edit_form'
                                          , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
                                          , 'visible'   : 0
                                          }
                                     )
                            },
                        )

def addContentPanels( self
           , id
           , title=''
           , description=''
            , panelsConfig=[]
           ):
    o=ContentPanels( id, title, description, panelsConfig )
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
    
    # the following 2 lines is to kill the default left and right slot in plone 
    left_slots = []
    right_slots = []
    
    security = ClassSecurityInfo()

    def __init__(self, id, title='', description='', panelsConfig=[]):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.description=description
        import copy
        self.panelsConfig = copy.deepcopy(panelsConfig)  # must deep copy!!
        if self.panelsConfig == []:
            self.addPage()
        self._p_changed = 1

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

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addPage' )
    def addPage(self, pageTitle='Untitled page'):
        """
        add a new page, it has two columns as default.
        return the new page index (from 0)
        """

        self.panelsConfig.append({'pageColumns': [],
                         'pageTitle': pageTitle,
                         'pageWidth':'95%',
                         'pageCellSpace':'0',
                         'pageCellPad':'10',
                         'pageAlign':'center',
                         'pageStylesheetFixed':[],
                         'pageStylesheetDynamic':[]})

        # add two default columns for the new page
        pageIndex = len(self.panelsConfig) - 1
        self.addColumn(pageIndex)
        self.addColumn(pageIndex)
        self._p_changed = 1
        return pageIndex

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addColumn' )
    def addColumn(self, pageIndex):
        self.panelsConfig[pageIndex]['pageColumns'].append({'columnWidth': '0',
                                                            'columnPanels':[] })
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'insertPanel' )
    def insertPanel(self, pageIndex, columnIndex, panelIndex, panelObjectPath, panelObjectType, panelSkin):
        ''' insert a new panel at panelIndex'''
        
        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'].\
                insert(panelIndex, {'panelSkin':panelSkin,
                        'panelObjectPath':panelObjectPath,
                        'panelObejctType':panelObjectType})
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

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'deleteColumn' )
    def deleteColumn(self, pageIndex, columnIndex):
        '''# delete column'''
        del self.panelsConfig[pageIndex]['pageColumns'][columnIndex]
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'deletePanel' )
    def deletePanel(self, pageIndex, columnIndex, panelIndex):
        ''' delete a Panel '''
        del self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changePanel' )
    def changePanel(self, pageIndex, columnIndex, panelIndex, panelObjectPath, panelObjectType, panelSkin):
        ''' change the skin of a existing panel '''
        
        if panelSkin == '':
            return

        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelSkin'] = panelSkin
        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelObjectPath'] = panelObjectPath
        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnPanels'][panelIndex]['panelObjectType'] = panelObjectType
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changeColumnWidth' )
    def changeColumnWidth(self, pageIndex, columnIndex, columnWidth):
        ''' change the width of a column '''
        if columnWidth == '':
            return None

        self.panelsConfig[pageIndex]['pageColumns'][columnIndex]['columnWidth'] = columnWidth
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'changePageInfo' )
    def changePageInfo(self, pageIndex, pageTitle, pageCellPad, pageCellSpace, pageWidth, pageAlign):
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
    
InitializeClass(ContentPanels)


import OFS.Moniker
from OFS.CopySupport import _cb_decode
from AccessControl import ModuleSecurityInfo


ModuleSecurityInfo('Products.CMFContentPanels.ContentPanels').declarePublic('getCopyedObjectsInfo')
def getCopyedObjectsInfo(context, REQUEST=None):
    '''
    get copyed object from cookie
    '''
    cp=None
    copyedObjectsInfo = []
    if REQUEST and REQUEST.has_key('__cp'):
                cp=REQUEST['__cp']
    if cp is None:
        pass
    else:
        try:
            cp=_cb_decode(cp)
            physicalRoot = context.getPhysicalRoot()
            for mdata in cp[1]:
                m = OFS.Moniker.loadMoniker(mdata)
                ob = m.bind(physicalRoot)
                copyedObjectsInfo.append( ('/'.join(ob.getPhysicalPath()), ob.Title() ) )
        except:
            pass
    return copyedObjectsInfo
