#-----------------------------------------------------------------------------
# Name:        QuickInstallerTool.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: QuickInstallerTool.py,v 1.48 2004/09/18 10:36:31 dreamcatcher Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import traceback
import os

import Globals
from Globals import HTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from ZODB.POSException import InvalidObjectReference

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from App.Common import package_home

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from InstalledProduct import InstalledProduct

from interfaces.portal_quickinstaller import IQuickInstallerTool
from exceptions import RuntimeError
from zLOG import LOG

try: 
    from zExceptions import NotFound
except ImportError:
    NotFound = 'NotFound'

from installer import install_from_xml

try:
    from zpi.zope import not_installed, hot_plug
    #print 'Packman support(hotplug) installed'
except ImportError:
    def not_installed(s): return []

class AlreadyInstalled(Exception):
    """ Would be nice to say what Product was trying to be installed """
    pass

def addQuickInstallerTool(self,REQUEST=None):
    """ """
    qt = QuickInstallerTool()
    self._setObject('portal_quickinstaller', qt, set_owner=0)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

class QuickInstallerTool(UniqueObject, ObjectManager, SimpleItem):

    __implements__ = IQuickInstallerTool

    meta_type = 'CMF QuickInstaller Tool'
    id = 'portal_quickinstaller'

    security = ClassSecurityInfo()

    manage_options=(
        {'label':'Install', 'action':'manage_installProductsForm'},
        ) + ObjectManager.manage_options

    security.declareProtected(ManagePortal, 'manage_installProductsForm')
    manage_installProductsForm = PageTemplateFile(
        'forms/install_products_form', globals(),
        __name__='manage_installProductsForm')

    security = ClassSecurityInfo()

    def __init__(self):
        self.id = 'portal_quickinstaller'

    security.declareProtected(ManagePortal, 'getInstallMethod')
    def getInstallMethod(self,productname):
        """ Return the installer method
        """
        for mod, func in (('Install','install'),
                          ('Install','Install'),
                          ('install','install'),
                          ('install','Install')):
            if productname in self.Control_Panel.Products.objectIds():
                productInCP = self.Control_Panel.Products[productname]

                if mod in productInCP.objectIds():
                    modFolder = productInCP[mod]
                    if func in modFolder.objectIds():
                        return modFolder[func]

            try:
                return ExternalMethod('temp', 'temp', productname+'.'+mod, func)
            except RuntimeError, msg:
                # external method can throw a bunch of these
                msg = "RuntimeError: %s" % msg
                LOG("Quick Installer Tool: ", 100, "%s" % productname, msg)
            except:
                # catch a string exception
                err = sys.exc_type
                #print err, sys.exc_type, sys.exc_value
                if err not in ("Module Error", NotFound):
                    msg = "%s: %s" % (err, sys.exc_value)
                    LOG("Quick Installer Tool: ", 100, "%s" % productname, msg)

        raise AttributeError, ('No Install method found for '
                               'product %s' % productname)

    security.declareProtected(ManagePortal, 'isProductInstallable')
    def isProductInstallable(self,productname):
        """Asks wether a product is installable by
        trying to get its install method
        """
        try:
            meth=self.getInstallMethod(productname)
            return 1
        except:
            return 0

    security.declareProtected(ManagePortal, 'isProductAvailable')
    isProductAvailable = isProductInstallable

    security.declareProtected(ManagePortal, 'listInstallableProducts')
    def listInstallableProducts(self,skipInstalled=1):
        """List candidate CMF products for
        installation -> list of dicts with keys:(id,hasError,status)
        """
        pids = self.Control_Panel.Products.objectIds() + not_installed(self)

        pids = [pid for pid in pids if self.isProductInstallable(pid)]

        if skipInstalled:
            installed=[p['id'] for p in self.listInstalledProducts(showHidden=1)]
            pids=[r for r in pids if r not in installed]

        res=[]
        for r in pids:
            p=self._getOb(r,None)
            if p:
                res.append({'id':r, 'status':p.getStatus(),
                            'hasError':p.hasError()})
            else:
                res.append({'id':r, 'status':'new', 'hasError':0})
        return res


    security.declareProtected(ManagePortal, 'listInstalledProducts')
    def listInstalledProducts(self, showHidden=0):
        """Returns a list of products that are installed -> list of
        dicts with keys:(id, hasError, status, isLocked, isHidden,
        installedVersion)
        """

        pids = [o.id for o in self.objectValues()
                if o.isInstalled() and (o.isVisible() or showHidden)]

        res=[]

        for r in pids:
            p = self._getOb(r,None)
            res.append({'id':r, 'status':p.getStatus(),
                        'hasError':p.hasError(),
                        'isLocked':p.isLocked(),
                        'isHidden':p.isHidden(),
                        'installedVersion':p.getInstalledVersion()})
        return res

    security.declareProtected(ManagePortal, 'getProductFile')
    def getProductFile(self,p,fname='readme.txt'):
        """Return the content of a file of the product
        case-insensitive, if it does not exist -> None
        """
        try:
            prodpath=self.Control_Panel.Products._getOb(p).home
        except AttributeError:
            return None

        #now list the directory to get the readme.txt case-insensitive
        try:
            files=os.listdir(prodpath)
        except OSError:
            return None

        for f in files:
            if f.lower()==fname:
                return open(os.path.join(prodpath,f)).read()

        return None

    security.declareProtected(ManagePortal, 'getProductReadme')
    getProductReadme=getProductFile

    security.declareProtected(ManagePortal, 'getProductVersion')
    def getProductVersion(self,p):
        """Return the version string stored in version.txt
        """

        res = self.getProductFile(p, 'version.txt')
        if res is not None:
            res = res.strip()
        return res


    security.declareProtected(ManagePortal, 'installProduct')
    def installProduct(self,p,locked=0,hidden=0,swallowExceptions=0):
        """Install a product by name
        """

        __traceback_info__ = (p,)
        
        if self.isProductInstalled(p):
            prod = self._getOb(p)
            msg = ('this product is already installed, '
                   'please uninstall before reinstalling it')
            prod.log(msg)
            return msg

        if p in not_installed(self):
            hot_plug(self, p)

        portal_types=getToolByName(self,'portal_types')
        portal_skins=getToolByName(self,'portal_skins')
        portal_actions=getToolByName(self,'portal_actions')
        portal_workflow=getToolByName(self,'portal_workflow')
        portal=getToolByName(self,'portal_url').getPortalObject()
        type_registry=getToolByName(self,'content_type_registry')

        leftslotsbefore=getattr(portal,'left_slots',[])
        rightslotsbefore=getattr(portal,'right_slots',[])
        registrypredicatesbefore=[pred[0] for pred in type_registry.listPredicates()]


        emid='install'+p
        typesbefore=portal_types.objectIds()
        skinsbefore=portal_skins.objectIds()
        actionsbefore=[a.id for a in portal_actions._actions]
        workflowsbefore=portal_workflow.objectIds()
        portalobjectsbefore=portal.objectIds()
        res=''
        status=None
        error=1
        install = self.getInstallMethod(p).__of__(portal)

        # Some heursitics to figure out if its already been installed
        if swallowExceptions:
            get_transaction().commit(1) # start a subtransaction,
                                        # commit what has happened so
                                        # far
        try:

            res=install()
            status='installed'
            error=0
            if swallowExceptions:
                get_transaction().commit(1)
        except InvalidObjectReference,e:
            raise
        except:
            tb=sys.exc_info()
            if str(tb[1]).endswith('already in use.'):
                self.error_log.raising(tb)
                res='this product has already been installed without Quickinstaller!'
                if not swallowExceptions:
                    raise AlreadyInstalled

            res+='failed:'+'\n'+'\n'.join(traceback.format_exception(*tb))
            self.error_log.raising(tb)

            # Try to avoid reference
            del tb

            if swallowExceptions:
                get_transaction().abort(1)   #this is very naughty
            else:
                raise


        typesafter=portal_types.objectIds()
        skinsafter=portal_skins.objectIds()
        actionsafter=portal_actions.objectIds()
        workflowsafter=portal_workflow.objectIds()
        portalobjectsafter=portal.objectIds()
        leftslotsafter=getattr(portal,'left_slots',[])
        rightslotsafter=getattr(portal,'right_slots',[])
        registrypredicatesafter=[pred[0] for pred in type_registry.listPredicates()]

        if callable(rightslotsafter):
            rightslotsafter = rightslotsafter()
        if callable(leftslotsafter):
            leftslotsafter = leftslotsafter()

        if callable(rightslotsbefore):
            rightslotsbefore = rightslotsbefore()
        if callable(leftslotsbefore):
            leftslotsbefore = leftslotsbefore()

        types=[t for t in typesafter if t not in typesbefore]
        skins=[s for s in skinsafter if s not in skinsbefore]
        actions=[a.id for a in portal_actions._actions
                 if a.id not in actionsbefore]
        workflows=[w for w in workflowsafter if w not in workflowsbefore]
        portalobjects=[a for a in portalobjectsafter
                       if a not in portalobjectsbefore]
        leftslots=[s for s in leftslotsafter if s not in leftslotsbefore]
        rightslots=[s for s in rightslotsafter if s not in rightslotsbefore]
        registrypredicates=[s for s in registrypredicatesafter
                            if s not in registrypredicatesbefore]

        msg=str(res)
        version=self.getProductVersion(p)
        # add the product
        try:
            if p in self.objectIds():
                p = getattr(self, p)
                p.update(types=types,
                         skins=skins,
                         actions=actions,
                         portalobjects=portalobjects,
                         workflows=workflows,
                         leftslots=leftslots,
                         rightslots=rightslots,
                         registrypredicates=registrypredicates,
                         installedversion=version,
                         logmsg=res,
                         status=status,
                         error=error,
                         locked=locked,
                         hidden=hidden)
            else:
                ip = InstalledProduct(p, types=types,
                                      skins=skins,
                                      actions=actions,
                                      portalobjects=portalobjects,
                                      workflows=workflows,
                                      leftslots=leftslots,
                                      rightslots=rightslots,
                                      registrypredicates=registrypredicates,
                                      installedversion=version,
                                      logmsg=res,
                                      status=status,
                                      error=error,
                                      locked=locked,
                                      hidden=hidden)
                self._setObject(p,ip)
        except InvalidObjectReference,e:
            raise
        except:
            tb=sys.exc_info()
            res+='failed:'+'\n'+'\n'.join(traceback.format_exception(*tb))
            self.error_log.raising(tb)

            # Try to avoid reference
            del tb

            if swallowExceptions:
                get_transaction().abort(1)   #this is very naughty
            else:
                raise

        return res

    security.declareProtected(ManagePortal, 'installProducts')
    def installProducts(self,products=[],stoponerror=0,REQUEST=None):
        """ """
        res = """
    Installed Products
    ====================
    """
        ok = 1
        # return products
        for p in products:
            res += p +':'
            try:
                r=self.installProduct(p,swallowExceptions=not stoponerror)
                res +='ok:\n'
                if r:
                    r += str(r)+'\n'
            except InvalidObjectReference,e:
                raise
            except Exception,e:
                ok=0
                if stoponerror:
                    raise
                res += 'failed:'+str(e)+'\n'
            except :
                ok=0
                if stoponerror:
                    raise
                res += 'failed\n'

        # New Part if it is accepted perhaps build it in in the loop above
        for p in products:
            data = install_from_xml(self, p)
            res += data

        if REQUEST :
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

        return res


    def isProductInstalled(self, productname):
        """Check wether a product is installed (by name)
        """
        o = self._getOb(productname, None)
        return o and o.isInstalled()


    security.declareProtected(ManagePortal, 'notifyInstalled')
    def notifyInstalled(self,p,locked=1,hidden=0,**kw):
        """Marks a product that has been installed
        without QuickInstaller as installed
        """

        if p in self.objectIds():
            p = getattr(self, p)
            p.update(locked=locked, hidden=hidden, **kw)
        else:
            ip = InstalledProduct(p,locked=locked, hidden=hidden, **kw)
            self._setObject(p,ip)

    security.declareProtected(ManagePortal, 'uninstallProducts')
    def uninstallProducts(self, products,
                          cascade=InstalledProduct.default_cascade,
                          REQUEST=None):
        """Removes a list of products
        """
        for pid in products:
            prod=getattr(self,pid)
            prod.uninstall(cascade=cascade)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(ManagePortal, 'reinstallProducts')
    def reinstallProducts(self, products, REQUEST=None):
        """Reinstalls a list of products, the main difference to
        ininstall/reinstall is that it does not remove portal objects
        created  during install (e.g. tools, etc.)
        """
        if type(products) in (type(''),type(u'')):
            products=[products]

        # only delete everything EXCEPT portalobjects (tools etc) for reinstall
        cascade=[c for c in InstalledProduct.default_cascade
                 if c != 'portalobjects']
        self.uninstallProducts(products, cascade)
        self.installProducts(products, stoponerror=1)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

InitializeClass(QuickInstallerTool)
