#-----------------------------------------------------------------------------
# Name:        InstalledProduct.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: InstalledProduct.py,v 1.22 2004/07/28 01:35:05 dreamcatcher Exp $
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from interfaces.portal_quickinstaller import IInstalledProduct
from installer import uninstall_from_xml


def updatelist(a,b):
    for l in b:
        if not l in a:
            a.append(l)

def delObjects(cont, ids):
    delids=[id for id in ids if hasattr(cont,id)]
    cont.manage_delObjects(delids)

class InstalledProduct(SimpleItem):
    """ class storing information about an installed product"""

    __implements__ = IInstalledProduct

    meta_type = "Installed Product"

    manage_options=(
        {'label':'View','action':'manage_installationInfo'},
        ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_installationInfo')
    manage_installationInfo = PageTemplateFile(
        'forms/installed_product_overview', globals(),
        __name__='manage_installationInfo')

    leftslots=[]
    rightslots=[]
    transcript=[]
    error=0 #error flag
    default_cascade=['types', 'skins', 'actions', 'portalobjects',
                     'workflows', 'slots', 'registrypredicates']

    def __init__(self, id, types=[], skins=[], actions=[],
                 portalobjects=[], workflows=[], leftslots=[],
                 rightslots=[], registrypredicates=[],
                 installedversion='', logmsg='', status='installed',
                 error=0, locked=0, hidden=0):
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
    def update(self, types=[], skins=[], actions=[], portalobjects=[],
               workflows=[], leftslots=[], rightslots=[],
               registrypredicates=[], installedversion='',
               logmsg='', status='installed', error=0,
               locked=0, hidden=0):

        #check for the availability of attributes before assiging
        for att in ['types', 'skins', 'actions', 'portalobjects',
                    'workflows', 'leftslots', 'rightslots',
                    'registrypredicates']:
            if not hasattr(self, att):
                setattr(self, att, [])

        updatelist(self.types,types)
        updatelist(self.skins,skins)
        updatelist(self.actions,actions)
        updatelist(self.portalobjects,portalobjects)
        updatelist(self.workflows,workflows)
        updatelist(self.leftslots,leftslots)
        updatelist(self.rightslots,rightslots)

        updatelist(self.registrypredicates,registrypredicates)
        self.transcript.insert(0, {'timestamp':DateTime(), 'msg':logmsg})
        self.locked=locked
        self.hidden=hidden
        self.installedversion=installedversion

        if status:
            self.status=status

        self.error=error

    security.declareProtected(ManagePortal, 'log')
    def log(self, logmsg):
        """Adds a log to the transcript
        """
        self.transcript.insert(0, {'timestamp':DateTime(), 'msg':logmsg})

    security.declareProtected(ManagePortal, 'hasError')
    def hasError(self):
        """Returns if the prod is in error state
        """
        return getattr(self, 'error', 0)

    security.declareProtected(ManagePortal, 'isLocked')
    def isLocked(self):
        """Is the product locked for uninstall
        """
        return getattr(self, 'locked', 0)

    security.declareProtected(ManagePortal, 'isHidden')
    def isHidden(self):
        """Is the product hidden
        """
        return getattr(self, 'hidden', 0)

    security.declareProtected(ManagePortal, 'isVisible')
    def isVisible(self):
        return not self.isHidden()

    security.declareProtected(ManagePortal, 'isInstalled')
    def isInstalled(self):
        return self.status=='installed'

    security.declareProtected(ManagePortal, 'getStatus')
    def getStatus(self):
        return self.status

    security.declareProtected(ManagePortal, 'getTypes')
    def getTypes(self):
        return self.types

    security.declareProtected(ManagePortal, 'getSkins')
    def getSkins(self):
        return self.skins

    security.declareProtected(ManagePortal, 'getActions')
    def getActions(self):
        return self.actions

    security.declareProtected(ManagePortal, 'getPortalObjects')
    def getPortalObjects(self):
        return self.portalobjects

    security.declareProtected(ManagePortal, 'getWorkflows')
    def getWorkflows(self):
        return self.workflows

    security.declareProtected(ManagePortal, 'getLeftSlots')
    def getLeftSlots(self):
        return self.leftslots

    security.declareProtected(ManagePortal, 'getRightSlots')
    def getRightSlots(self):
        return self.rightslots

    security.declareProtected(ManagePortal, 'getSlots')
    def getSlots(self):
        return self.leftslots+self.rightslots

    security.declareProtected(ManagePortal, 'getRegistryPredicates')
    def getRegistryPredicates(self):
        """Return the custom entries in the content_type_registry
        """
        return getattr(self, 'registrypredicates', [])

    security.declareProtected(ManagePortal, 'getTranscriptAsText')
    def getTranscriptAsText(self):
        if getattr(self,'transcript',None):
            msgs = [t['timestamp'].ISO()+'\n'+str(t['msg'])
                    for t in self.transcript]
            return '\n=============\n'.join(msgs)
        else:
            return 'no messages'

    security.declareProtected(ManagePortal, 'getUninstallMethod')
    def getUninstallMethod(self):
        """ returns the uninstaller method """

        try:
            productInCP = self.Control_Panel.Products[self.id]
        except KeyError:
            return None

        for mod, func in (('Install','uninstall'),
                          ('Install','Uninstall'),
                          ('install','uninstall'),
                          ('install','Uninstall')):
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
    def uninstall(self,cascade=default_cascade,REQUEST=None):
        """Uninstalls the product and removes its dependencies
        """

        portal=getToolByName(self,'portal_url').getPortalObject()

        # XXX eventually we will land Event system and could remove
        # this 'removal_inprogress' hack
        if self.isLocked() and getattr(portal, 'removal_inprogress', 0):
            raise ValueError, 'The product is locked and cannot be uninstalled!'

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
            portal_workflow=getToolByName(self, 'portal_workflow')
            delObjects(portal_workflow, self.workflows)

        if 'slots' in cascade:
            if self.leftslots:
                portal.left_slots=[s for s in portal.left_slots
                                   if s not in self.leftslots]
            if self.rightslots:
                portal.right_slots=[s for s in portal.right_slots
                                    if s not in self.rightslots]

        if 'registrypredicates' in cascade:
            registry=getToolByName(self,'content_type_registry')
            predicates=getattr(self,'registrypredicates',[])
            for p in predicates:
                registry.removePredicate(p)


        self.status='uninstalled'
        self.log('uninstalled\n'+str(res))

        # New part
        uninstall_from_xml(portal,self.id)

        if REQUEST and REQUEST.get('nextUrl',None):
            return REQUEST.RESPONSE.redirect(REQUEST['nextUrl'])

    security.declareProtected(ManagePortal, 'getInstalledVersion')
    def getInstalledVersion(self):
        """Return the version of the product in the moment of installation
        """
        return getattr(self, 'installedversion', None)

InitializeClass(InstalledProduct)
