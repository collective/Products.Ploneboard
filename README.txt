CMFQuickInstallerTool
==================

Features
----------

CMFQuickInstallerTool is a facility for comfortable activation/deactivation
of CMF compliant products inside a CMF site.

Therefore it has to be installed as a tool inside a CMF portal,
where it stores the information about the installed products.

The requirements for a product to be installable with
QuickInstallerTool are quite simple (almost all existing CMF 
products fulfill them):

  External Product:  The product has to implement an external 
                     method 'install' in a python module 'Install.py' 
                     in its Extensions directory.

  TTW Product: The product has to have a 'Install' folder
               and have a python script titled 'install' inside
               that folder.

Products can be uninstalled and QuickInstellerTool removes
the following items a product creates during install:

portal types,
portal skins,
portal actions,
portalobjects (objects created in the root of the portal),
workflows,
left and right slots (also checks them only for the portal)

Attention: QuickInstallerTool just tracks which objects are 
ADDED, but not what is changed or deleted.

second Attention:
QuickInstallerTool just can uninstall products that are 
installed via QuickInstallerTool

Installation
------------

- Drop the CMFQuickInstallerTool into the Products directory.

- inside the portal instanciate a CMF QuickInstaller Tool

- Happy debian users may apt-get install the Quick Installer by 
adding the following line to their /etc/apt/sources.list file :

deb ftp://ftp.logilab.org/pub/debian unstable/

Usage:
--------

in the ZMI click on portal_quickinstaller.
the management screen allows you to select products for
installation and uninstallation.
you can browse into the installed products and see what
they created and see the logs of the install process.

for Plone there will be an interface inside the portal so that
it is not necessary to enter thr ZMI for product management

API
-------

QuickInstaller is also intended to be called from other modules
in order to automate installing of application.
For API reference see interfaces/portal_quickinstaller.py

Customized uninstall
--------------------

In order to use a customize uninstall, the following
requirements must be met:

  External Product:  The product has to implement an external 
                     method 'uninstall in a python module 'Install.py' 
                     in its Extensions directory.

  TTW Product: The product has to have a 'Install' folder
               and have a python script titled 'uninstall' inside
               that folder.  This script must also accept a 'portal'
               parameter.

Please note that the customized uninstall method is invoked before
(and in addition to) the standard removal of objects.

Install:
--------

  install(portal) or install(portal, reinstall)

Uninstall:
----------

  uninstall(portal) or uninstall(portal, reinstall)

Reinstall
---------

Reinstalling a product invokes uninstall() and install(). If you have special
code which should work differently on reinstall than uninstall/install you can
add a second argument to the install or uninstall method named 'reinstall' which
is true only for a reinstallation. In most cases you shouldn't react differently
when reinstalling!

Special Hooks
-------------

afterInstall:  Called after a product is installed and the changes are saved
               into the product instance.
               The method is called between install() and recoding the installed
               objects.
beforeInstall: Called before a product is uninstalled. It may change the
               cascade containing which object types should be cleared.
               The method is called after uninstall() but before the cascading
               removing of installed objects.
API:
  out = afterInstall(portal, reinstall=reinstall, qi_product)
  out, cascade = beforeUninstall(portal, reinstall, qi_product, cascade)

Flow: 
  install(), <record installation>, afterInstall()
  uninstall(), beforeUninstall(), <cascade remove>
