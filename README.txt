CMFQuickInstallerTool
==================

Features
----------

This tool is independent from the former CMFQuickInstaller.
The main difference to CMFQuickInstaller the tracking of
what a product creates during install. 

Therefore it has to be installed as a tool inside a CMF portal,
where it stores the infotmation about the installed products.

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
------------
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
