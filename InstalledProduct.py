#-----------------------------------------------------------------------------
# Name:        InstalledProduct.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: InstalledProduct.py,v 1.14 2003/10/05 16:38:56 zworkb Exp $
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

from interfaces.portal_quickinstaller import IInstalledProduct

def updatelist(a,b):
    for l in b:
        if not l in a:
            a.append(l)
            
def delObjects(cont,ids):
    delids=[id for id in ids if hasattr(cont,id)]
    cont.manage_delObjects(delids)

class InstalledProduct(SimpleItem):
    ''' class storing information about an installed product'''

    __implements__ = IInstalledProduct
    
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
        self.uninstall()
        
    def __init__(self,id,types=[],skins=[],actions=[],portalobjects=[],
        workflows=[],leftslots=[],rightslots=[],registrypredicates=[],installedversion='',logmsg='',status='installed',
        error=0,locked=0, hidden=0):
        self.id=id
        self.types=types
        self.skins=skins
        self.actions=actions
        self.portalobjects=portalobjects
        self.workflows=workflows
        self.leftslots=leftslots
        self.rightslots=rightslots
        self.transcript=[{'timestamp':DateTime(),'msg':logmsg}]
        self.locked=locked
        self.hidden=hidden
        self.registrypredicates=registrypredicates
        self.installedversion=installedversion
        
        if status:
            self.status=status
        else:
            self.status='new'
            
        self.error=error

    security.declareProtected(ManagePortal, 'update')
    def update(self,types=[],skins=[],actions=[],portalobjects=[],workflows=[],
        leftslots=[],rightslots=[],registrypredicates=[],installedversion='',logmsg='',status='installed',error=0,locked=0,hidden=0):
        updatelist(self.types,types)
        updatelist(self.skins,skins)
        updatelist(self.actions,actions)
        updatelist(self.portalobjects,portalobjects)
        updatelist(self.workflows,workflows)
        updatelist(self.leftslots,leftslots)
        updatelist(self.rightslots,rightslots)
        updatelist(self.registrypredicates,registrypredicates)
        self.transcript.insert(0,{'timestamp':DateTime(),'msg':logmsg})
        self.locked=locked
        self.hidden=hidden
        self.installedversion=installedversion
        
        if status:
            self.status=status
            
        self.error=error
        
    def log(self,logmsg):
        ''' adds a log to the transcript '''
        self.transcript.insert(0,{'timestamp':DateTime(),'msg':logmsg})
        
    def hasError(self):
        ''' returns if the prod is in error state '''
        return getattr(self,'error',0)
    
    def isLocked(self):
        ''' is the product locked for uninstall '''
        return getattr(self,'locked',0)

    def isHidden(self):
        ''' is the product hidden'''
        return getattr(self,'hidden',0)
    
    def isVisible(self):
        return not self.isHidden()
    
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

    def getRegistryPredicates(self):
        ''' returns the custom entries in the content_type_registry '''
        return getattr(self,'registrypredicates',[])
    
    def getTranscriptAsText(self):
        if getattr(self,'transcript',None):
            return '\n=============\n'.join([t['timestamp'].ISO()+'\n'+str(t['msg']) for t in self.transcript])
        else:
            return 'no messages'

    def getUninstallMethod(self):
        ''' returns the uninstaller method '''
        
        productInCP = self.Control_Panel.Products[self.id]
        
        for mod,func in (('Install','uninstall'),('Install','Uninstall'),('install','uninstall'),('install','Uninstall')):
            if mod in productInCP.objectIds():
                modFolder = productInCP[mod]
                if func in modFolder.objectIds():
                    return modFolder[func]

            try:
                return ExternalMethod('temp','temp',self.id+'.'+mod, func)    
            except:
                pass
            
        return None

    security.declareProtected(ManagePortal, 'uninstall')
    def uninstall(self,cascade=['types','skins','actions','portalobjects','workflows','slots','registrypredicates'],REQUEST=None):
        '''uninstalls the prod and removes its deps'''

        if self.isLocked():
            raise ValueError, 'The product is locked and cannot be uninstalled!'
        
        portal=getToolByName(self,'portal_url').getPortalObject()
        res=''

        uninstaller=self.getUninstallMethod()
        
        if uninstaller:
            res=uninstaller(portal)
            
        if 'types' in cascade:
            portal_types=getToolByName(self,'portal_types')
            delObjects(portal_types, self.types)

        if 'skins' in cascade:
            portal_skins=getToolByName(self,'portal_skins')
            delObjects(portal_skins, self.skins)
            
        if 'actions' in cascade:
            portal_actions=getToolByName(self,'portal_actions')
            actids= [o.id.lower() for o in portal_actions._actions]
            delactions=[actids.index(id) for id in self.actions if id in actids]
            if delactions: portal_actions.deleteActions(delactions)

        if 'portalobjects' in cascade:
            delObjects(portal, self.portalobjects)

        if 'workflows' in cascade:
            portal_workflow=getToolByName(self,'portal_workflow')
            delObjects(portal_workflow, self.workflows)
            
        if 'slots' in cascade:
            if self.leftslots: 
                portal.left_slots=[s for s in portal.left_slots if s not in self.leftslots]
            if self.rightslots:
                portal.right_slots=[s for s in portal.right_slots if s not in self.rightslots]

        if 'registrypredicates' in cascade:
            registry=getToolByName(self,'content_type_registry')
            predicates=getattr(self,'registrypredicates',[])
            for p in predicates:
                registry.removePredicate(p)
                    
            
        self.status='uninstalled'
        self.log('uninstalled\n'+str(res))
        
        if REQUEST and REQUEST.get('nextUrl',None):
            return REQUEST.RESPONSE.redirect(REQUEST['nextUrl'])
        
    def getInstalledVersion(self):
        ''' returns the version of the prod in the moment of installation '''
        return getattr(self,'installedversion',None)    
    
