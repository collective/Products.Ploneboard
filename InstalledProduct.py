#-----------------------------------------------------------------------------
# Name:        QuickInstallerTool.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: InstalledProduct.py,v 1.2 2003/02/16 13:09:22 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import os
import Globals
from DateTime import DateTime
from App.Common import package_home

from Globals import HTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent,Implicit

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate


def updatelist(a,b):
    for l in b:
        if not l in a:
            a.append(l)
            

class InstalledProduct(SimpleItem):
    ''' class storing information about an installed product'''

    meta_type="Installed Product"
    manage_options=(
        {'label':'view','action':'index_html'},
        ) 
    index_html=ZopePageTemplate('installForm',open(os.path.join(package_home(globals()),'forms','installed_product_overview.pt')).read())
    security = ClassSecurityInfo()

    leftslots=[]
    rightslots=[]
    transcript=[]
    error=0 #error flag
    
    def manage_beforeDelete(self,object,container):
        print 'beforedel'
        self.uninstall()
        
    def __init__(self,id,types,skins,actions,portalobjects,workflows,leftslots,rightslots,logmsg,status='installed',error=0):
        self.id=id
        self.types=types
        self.skins=skins
        self.actions=actions
        self.portalobjects=portalobjects
        self.workflows=workflows
        self.leftslots=leftslots
        self.rightslots=rightslots
        self.transcript=[{'timestamp':DateTime(),'msg':logmsg}]
        
        if status:
            self.status=status
        else:
            self.status='new'
            
        self.error=error

    security.declareProtected(ManagePortal, 'update')
    def update(self,types,skins,actions,portalobjects,workflows,leftslots,rightslots,logmsg,status='installed',error=0):
        updatelist(self.types,types)
        updatelist(self.skins,skins)
        updatelist(self.actions,actions)
        updatelist(self.portalobjects,portalobjects)
        updatelist(self.workflows,workflows)
        updatelist(self.leftslots,leftslots)
        updatelist(self.rightslots,rightslots)
        self.transcript.insert(0,{'timestamp':DateTime(),'msg':logmsg})
        
        if status:
            self.status=status
            
        self.error=error
        
    def log(self,logmsg):
        ''' adds a log to the transcript '''
        self.transcript.insert(0,{'timestamp':DateTime(),'msg':logmsg})
        
    def hasError(self):
        ''' returns if the prod is in error state '''
        return getattr(self,'error',0)
    
    def isInstalled(self):
        return self.status=='installed'
    
    def getStatus(self):
        return self.status
    
    def getTypes(self):
        return self.types
    
    def getSkins(self):
        return self.skins
    
    def getActions(self):
        return self.actions
    
    def getPortalObjects(self):
        return self.portalobjects
    
    def getWorkflows(self):
        return self.workflows
    
    def getLeftSlots(self):
        return self.leftslots
    
    def getRightSlots(self):
        return self.rightslots
    
    def getSlots(self):
        return self.leftslots+self.rightslots
    
    def getTranscriptAsText(self):
        if getattr(self,'transcript',None):
            return '\n=============\n'.join([t['timestamp'].ISO()+'\n'+str(t['msg']) for t in self.transcript])
        else:
            return 'no messages'

    security.declareProtected(ManagePortal, 'uninstall')
    def uninstall(self,cascade=['types','skins','actions','portalobjects','workflows','slots'],REQUEST=None):
        '''uninstalls the prod and removes its deps'''

        portal=getToolByName(self,'portal_url').getPortalObject()

        if 'types' in cascade:
            portal_types=getToolByName(self,'portal_types')
            portal_types.manage_delObjects(self.types)

        if 'skins' in cascade:
            portal_skins=getToolByName(self,'portal_skins')
            portal_skins.manage_delObjects(self.skins)
            
        if 'actions' in cascade:
            portal_actions=getToolByName(self,'portal_actions')
            actids= [o.id.lower() for o in portal_actions._actions]
            delactions=[actids.index(id) for id in self.actions]
            if delactions: portal_actions.deleteActions(delactions)

        if 'portalobjects' in cascade:
            portal.manage_delObjects(self.portalobjects)

        if 'workflows' in cascade:
            portal_workflow=getToolByName(self,'portal_workflow')
            portal_workflow.manage_delObjects(self.workflows)
            
        if 'slots' in cascade:
            if self.leftslots: 
                portal.leftslots=[s for s in portal.leftslots if s not in self.leftslots]
            if self.rightslots:
                portal.rightslots=[s for s in portal.rightslots if s not in self.rightslots]
            
        self.status='uninstalled'
        
        if REQUEST and REQUEST.get('nextUrl',None):
            return REQUEST.RESPONSE.redirect(REQUEST['nextUrl'])
        
    
    